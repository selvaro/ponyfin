\c ponyfin;

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'llm') THEN
      CREATE ROLE llm LOGIN PASSWORD '0000123450000';
   END IF;
END
$$;

CREATE SCHEMA IF NOT EXISTS llm_data;

CREATE OR REPLACE VIEW llm_data.incomes AS
SELECT id, amount, currency, date, source
FROM public.incomes
WHERE user_id = current_setting('app.current_user_id')::bigint;

CREATE OR REPLACE VIEW llm_data.expenses AS
SELECT id, amount, currency, date, description, category_id
FROM public.expenses
WHERE user_id = current_setting('app.current_user_id')::bigint;

CREATE OR REPLACE VIEW llm_data.categories AS
SELECT id, name, description
FROM public.categories
WHERE user_id = current_setting('app.current_user_id')::bigint;

CREATE OR REPLACE VIEW llm_data.budgets AS
SELECT id, month, year, amount, category_id
FROM public.budgets
WHERE user_id = current_setting('app.current_user_id')::bigint;

CREATE OR REPLACE FUNCTION llm_data.incomes_insert_trigger()
RETURNS trigger AS $$
BEGIN
   INSERT INTO public.incomes (amount, currency, date, source, user_id)
   VALUES (NEW.amount, NEW.currency, NEW.date, NEW.source, current_setting('app.current_user_id')::bigint)
   RETURNING id INTO NEW.id;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER incomes_insert_instead
INSTEAD OF INSERT ON llm_data.incomes
FOR EACH ROW EXECUTE FUNCTION llm_data.incomes_insert_trigger();

CREATE OR REPLACE FUNCTION llm_data.incomes_update_trigger()
RETURNS trigger AS $$
BEGIN
   UPDATE public.incomes
   SET amount   = NEW.amount,
       currency = NEW.currency,
       date     = NEW.date,
       source   = NEW.source
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER incomes_update_instead
INSTEAD OF UPDATE ON llm_data.incomes
FOR EACH ROW EXECUTE FUNCTION llm_data.incomes_update_trigger();

CREATE OR REPLACE FUNCTION llm_data.incomes_delete_trigger()
RETURNS trigger AS $$
BEGIN
   DELETE FROM public.incomes
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER incomes_delete_instead
INSTEAD OF DELETE ON llm_data.incomes
FOR EACH ROW EXECUTE FUNCTION llm_data.incomes_delete_trigger();

CREATE OR REPLACE FUNCTION llm_data.expenses_insert_trigger()
RETURNS trigger AS $$
BEGIN
   INSERT INTO public.expenses (amount, currency, date, description, category_id, user_id)
   VALUES (NEW.amount, NEW.currency, NEW.date, NEW.description, NEW.category_id, current_setting('app.current_user_id')::bigint)
   RETURNING id INTO NEW.id;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER expenses_insert_instead
INSTEAD OF INSERT ON llm_data.expenses
FOR EACH ROW EXECUTE FUNCTION llm_data.expenses_insert_trigger();

CREATE OR REPLACE FUNCTION llm_data.expenses_update_trigger()
RETURNS trigger AS $$
BEGIN
   UPDATE public.expenses
   SET amount      = NEW.amount,
       currency    = NEW.currency,
       date        = NEW.date,
       description = NEW.description,
       category_id = NEW.category_id
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER expenses_update_instead
INSTEAD OF UPDATE ON llm_data.expenses
FOR EACH ROW EXECUTE FUNCTION llm_data.expenses_update_trigger();

CREATE OR REPLACE FUNCTION llm_data.expenses_delete_trigger()
RETURNS trigger AS $$
BEGIN
   DELETE FROM public.expenses
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER expenses_delete_instead
INSTEAD OF DELETE ON llm_data.expenses
FOR EACH ROW EXECUTE FUNCTION llm_data.expenses_delete_trigger();

CREATE OR REPLACE FUNCTION llm_data.categories_insert_trigger()
RETURNS trigger AS $$
BEGIN
   INSERT INTO public.categories (name, description, user_id)
   VALUES (NEW.name, NEW.description, current_setting('app.current_user_id')::bigint)
   RETURNING id INTO NEW.id;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER categories_insert_instead
INSTEAD OF INSERT ON llm_data.categories
FOR EACH ROW EXECUTE FUNCTION llm_data.categories_insert_trigger();

CREATE OR REPLACE FUNCTION llm_data.categories_update_trigger()
RETURNS trigger AS $$
BEGIN
   UPDATE public.categories
   SET name        = NEW.name,
       description = NEW.description
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER categories_update_instead
INSTEAD OF UPDATE ON llm_data.categories
FOR EACH ROW EXECUTE FUNCTION llm_data.categories_update_trigger();

CREATE OR REPLACE FUNCTION llm_data.categories_delete_trigger()
RETURNS trigger AS $$
BEGIN
   DELETE FROM public.categories
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER categories_delete_instead
INSTEAD OF DELETE ON llm_data.categories
FOR EACH ROW EXECUTE FUNCTION llm_data.categories_delete_trigger();

CREATE OR REPLACE FUNCTION llm_data.budgets_insert_trigger()
RETURNS trigger AS $$
BEGIN
   INSERT INTO public.budgets (month, year, amount, category_id, user_id)
   VALUES (NEW.month, NEW.year, NEW.amount, NEW.category_id, current_setting('app.current_user_id')::bigint)
   RETURNING id INTO NEW.id;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER budgets_insert_instead
INSTEAD OF INSERT ON llm_data.budgets
FOR EACH ROW EXECUTE FUNCTION llm_data.budgets_insert_trigger();

CREATE OR REPLACE FUNCTION llm_data.budgets_update_trigger()
RETURNS trigger AS $$
BEGIN
   UPDATE public.budgets
   SET month      = NEW.month,
       year       = NEW.year,
       amount     = NEW.amount,
       category_id= NEW.category_id
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER budgets_update_instead
INSTEAD OF UPDATE ON llm_data.budgets
FOR EACH ROW EXECUTE FUNCTION llm_data.budgets_update_trigger();

CREATE OR REPLACE FUNCTION llm_data.budgets_delete_trigger()
RETURNS trigger AS $$
BEGIN
   DELETE FROM public.budgets
   WHERE id = OLD.id AND user_id = current_setting('app.current_user_id')::bigint;
   RETURN OLD;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp;

CREATE TRIGGER budgets_delete_instead
INSTEAD OF DELETE ON llm_data.budgets
FOR EACH ROW EXECUTE FUNCTION llm_data.budgets_delete_trigger();

REVOKE ALL ON SCHEMA public FROM llm;
REVOKE ALL ON DATABASE ponyfin FROM llm;

GRANT USAGE ON SCHEMA llm_data TO llm;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA llm_data TO llm;

ALTER ROLE llm SET search_path = llm_data;

