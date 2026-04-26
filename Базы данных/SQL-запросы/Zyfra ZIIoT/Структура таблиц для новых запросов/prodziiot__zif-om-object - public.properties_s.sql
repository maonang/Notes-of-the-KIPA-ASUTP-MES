CREATE TABLE IF NOT EXISTS public.properties_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    isdeleted boolean NOT NULL DEFAULT false,
    valuetypeid uuid NOT NULL,
    uomid uuid NOT NULL,
    propertyprimitiveid uuid NOT NULL,
    objectid uuid NOT NULL,
    datatypeid uuid NOT NULL,
    hierarchyscopeids uuid[],
    propertytype smallint,
    path character varying COLLATE pg_catalog."default",
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    CONSTRAINT properties_s_pk_new PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT properties_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.properties_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT properties_s_properties_h_id_fk FOREIGN KEY (id)
        REFERENCES public.properties_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT properties_s_propertyprimitives_h_id_fk FOREIGN KEY (propertyprimitiveid)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.properties_s
    OWNER to "prodziiot__zif-om-object";

REVOKE ALL ON TABLE public.properties_s FROM prodziiot__read-role;

GRANT ALL ON TABLE public.properties_s TO prodziiot__debezium;

GRANT SELECT ON TABLE public.properties_s TO "prodziiot__read-role";

GRANT ALL ON TABLE public.properties_s TO "prodziiot__write-role";

GRANT ALL ON TABLE public.properties_s TO "prodziiot__zif-om-object";

GRANT ALL ON TABLE public.properties_s TO "prodziiot__zif-om-properties-view";
-- Index: properties_s_hierarchyscopeid_gin_idx

-- DROP INDEX IF EXISTS public.properties_s_hierarchyscopeid_gin_idx;

CREATE INDEX IF NOT EXISTS properties_s_hierarchyscopeid_gin_idx
    ON public.properties_s USING gin
    (hierarchyscopeids)
    TABLESPACE pg_default;
-- Index: properties_s_id_idx

-- DROP INDEX IF EXISTS public.properties_s_id_idx;

CREATE INDEX IF NOT EXISTS properties_s_id_idx
    ON public.properties_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;
-- Index: properties_s_name_idx

-- DROP INDEX IF EXISTS public.properties_s_name_idx;

CREATE INDEX IF NOT EXISTS properties_s_name_idx
    ON public.properties_s USING gin
    (name COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default;
-- Index: properties_s_objectid_index

-- DROP INDEX IF EXISTS public.properties_s_objectid_index;

CREATE INDEX IF NOT EXISTS properties_s_objectid_index
    ON public.properties_s USING btree
    (objectid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: properties_s_parentid_index

-- DROP INDEX IF EXISTS public.properties_s_parentid_index;

CREATE INDEX IF NOT EXISTS properties_s_parentid_index
    ON public.properties_s USING btree
    (parentid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: properties_s_propertyprimitiveid_index

-- DROP INDEX IF EXISTS public.properties_s_propertyprimitiveid_index;

CREATE INDEX IF NOT EXISTS properties_s_propertyprimitiveid_index
    ON public.properties_s USING btree
    (propertyprimitiveid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: properties_s_tt_idx

-- DROP INDEX IF EXISTS public.properties_s_tt_idx;

CREATE INDEX IF NOT EXISTS properties_s_tt_idx
    ON public.properties_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;

-- Trigger: properties_s_insert

-- DROP TRIGGER IF EXISTS properties_s_insert ON public.properties_s;

CREATE OR REPLACE TRIGGER properties_s_insert
    AFTER INSERT
    ON public.properties_s
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)
    EXECUTE FUNCTION public.properties_s_insert();