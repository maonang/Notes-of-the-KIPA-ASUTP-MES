CREATE TABLE IF NOT EXISTS public.propertyprimitives_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    isdeleted boolean NOT NULL DEFAULT false,
    description character varying(255) COLLATE pg_catalog."default",
    code character varying(255) COLLATE pg_catalog."default" NOT NULL,
    uomid uuid NOT NULL,
    valuetypeid uuid NOT NULL,
    datatypeid uuid NOT NULL,
    hierarchyscopeids uuid[],
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    path character varying COLLATE pg_catalog."default",
    CONSTRAINT propertyprimitives_new_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT propertyprimitives_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT propertyprimitives_s_propertyprimitives_h_id_fk FOREIGN KEY (id)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS propertyprimitives_s_hierarchyscopeid_gin_idx
    ON public.propertyprimitives_s USING gin
    (hierarchyscopeids)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS propertyprimitives_s_id_idx
    ON public.propertyprimitives_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;

CREATE INDEX IF NOT EXISTS propertyprimitives_s_parentid_index
    ON public.propertyprimitives_s USING btree
    (parentid ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS propertyprimitives_s_tt_idx
    ON public.propertyprimitives_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;

CREATE OR REPLACE TRIGGER propertyprimitives_s_insert
    AFTER INSERT
    ON public.propertyprimitives_s
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)
    EXECUTE FUNCTION public.propertyprimitives_s_insert();
...