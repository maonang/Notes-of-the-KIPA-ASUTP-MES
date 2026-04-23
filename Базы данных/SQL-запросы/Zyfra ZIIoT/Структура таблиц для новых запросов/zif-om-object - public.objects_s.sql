CREATE TABLE IF NOT EXISTS public.objects_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    objectprototypeid uuid,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    description character varying(255) COLLATE pg_catalog."default",
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    hierarchyscopeids uuid[],
    classid uuid,
    path character varying COLLATE pg_catalog."default",
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    CONSTRAINT objects_new_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT objects_s_objectprototypeid_fkey FOREIGN KEY (objectprototypeid)
        REFERENCES public.objectprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT objects_s_objects_h_id_fk FOREIGN KEY (id)
        REFERENCES public.objects_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT objects_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.objects_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.objects_s
    OWNER to "prodziiot__zif-om-object";

REVOKE ALL ON TABLE public.objects_s FROM prodziiot__read-role;

GRANT ALL ON TABLE public.objects_s TO prodziiot__debezium;

GRANT SELECT ON TABLE public.objects_s TO "prodziiot__read-role";

GRANT ALL ON TABLE public.objects_s TO "prodziiot__write-role";

GRANT ALL ON TABLE public.objects_s TO "prodziiot__zif-om-object";

GRANT ALL ON TABLE public.objects_s TO "prodziiot__zif-om-properties-view";
-- Index: objects_s_hierarchyscopeid_gin_idx

-- DROP INDEX IF EXISTS public.objects_s_hierarchyscopeid_gin_idx;

CREATE INDEX IF NOT EXISTS objects_s_hierarchyscopeid_gin_idx
    ON public.objects_s USING gin
    (hierarchyscopeids)
    TABLESPACE pg_default;
-- Index: objects_s_id_idx

-- DROP INDEX IF EXISTS public.objects_s_id_idx;

CREATE INDEX IF NOT EXISTS objects_s_id_idx
    ON public.objects_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;
-- Index: objects_s_name_idx

-- DROP INDEX IF EXISTS public.objects_s_name_idx;

CREATE INDEX IF NOT EXISTS objects_s_name_idx
    ON public.objects_s USING gin
    (name COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default;
-- Index: objects_s_objectprototypeid_index

-- DROP INDEX IF EXISTS public.objects_s_objectprototypeid_index;

CREATE INDEX IF NOT EXISTS objects_s_objectprototypeid_index
    ON public.objects_s USING btree
    (objectprototypeid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: objects_s_parentid_index

-- DROP INDEX IF EXISTS public.objects_s_parentid_index;

CREATE INDEX IF NOT EXISTS objects_s_parentid_index
    ON public.objects_s USING btree
    (parentid ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: objects_s_tt_idx

-- DROP INDEX IF EXISTS public.objects_s_tt_idx;

CREATE INDEX IF NOT EXISTS objects_s_tt_idx
    ON public.objects_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;

-- Trigger: objects_s_insert

-- DROP TRIGGER IF EXISTS objects_s_insert ON public.objects_s;

CREATE OR REPLACE TRIGGER objects_s_insert
    AFTER INSERT
    ON public.objects_s
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)
    EXECUTE FUNCTION public.objects_s_insert();