import json
from datetime import datetime
from os import getenv

import pytz
from db import log_tools
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from templates import response_template, system_prompt
from tools import TOOLS_JSON, run_tool

load_dotenv()


def get_current_timestamptz():
    kyiv_tz = pytz.timezone("Europe/Kyiv")
    current_time = datetime.now(kyiv_tz)
    return current_time.strftime("%Y-%m-%d %H:%M:%S%z")


tools_called = []


def make_response(user_id, question):
    response = run_full_chain(user_id, question)

    log_tools(
        user_id=user_id,
        question=question,
        tools_called=response["tools_called"],
        tools_results=response["tools_results"],
        response=response["answer"],
    )
    global tools_called
    tools_called = []
    return {"answer": response["answer"]}


def run_full_chain(user_id, question):
    llm = ChatGroq(
        model=getenv("MODEL_NAME"),
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt.format(
                    tools_json=json.dumps(TOOLS_JSON),
                    current_time=get_current_timestamptz(),
                )
                .replace("{", "{{")
                .replace("}", "}}"),
            ),
            ("human", "{question}\nPrevious tool results: {tool_results}"),
        ]
    )

    def execute_tool(vars):
        tool_results = []
        if isinstance(vars, dict):
            tool_calls = vars.get("tool_calls", [])
        else:
            tool_calls = getattr(vars, "tool_calls", [])

        if tool_calls:
            for tool_call in tool_calls:
                global tools_called
                args = (
                    tool_call["args"]
                    if isinstance(tool_call, dict)
                    else json.loads(tool_call.args)
                )
                tool_name = (
                    tool_call["name"] if isinstance(tool_call, dict) else tool_call.name
                )
                tools_called.append(f"Tool called: {tool_name} with arguments: {args}")
                print(f"{user_id}; {tool_name}; {args}", flush=True)
                result = run_tool(user_id, tool_name, args)
                print(result, flush=True)
                tool_results.append({"tool": tool_name, "result": result})
                print(tool_results, flush=True)
            return {
                "tool_results": tool_results,
                "tool_calls": [],
            }
        return {
            "tool_results": tool_results,
            "tool_calls": [],
        }

    chain = (
        prompt
        | llm.bind(tools=json.loads(TOOLS_JSON), tool_choice="auto")
        | execute_tool
    )

    max_iterations = 5
    state = {"question": question, "tool_results": []}
    for _ in range(max_iterations):
        result = chain.invoke(state)
        state["tool_results"] = result["tool_results"]
        if not result.get("tool_calls"):
            break

    final_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                response_template.format(
                    results=json.dumps(state["tool_results"])
                    .replace("{", "{{")
                    .replace("}", "}}"),
                ),
            ),
            ("human", "{question}\nTool results: {tool_results}"),
        ]
    )
    final_chain = final_prompt | llm | StrOutputParser()
    final_answer = final_chain.invoke(
        {
            "question": question,
            "tool_results": json.dumps(state["tool_results"])
            .replace("{", "{{")
            .replace("}", "}}"),
        }
    )

    return {
        "answer": final_answer,
        "tools_called": json.dumps(tools_called),
        "tools_results": json.dumps(state["tool_results"]),
    }
