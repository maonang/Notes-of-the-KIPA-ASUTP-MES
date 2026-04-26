CREATE TABLE IF NOT EXISTS public.classes_s
(
    id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    isdeleted boolean NOT NULL DEFAULT false,
    description character varying(255) COLLATE pg_catalog."default",
    code character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'code'::character varying,
    isabstract boolean NOT NULL DEFAULT false,
    parentid uuid,
    hierarchyscopeids uuid[],
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    CONSTRAINT classes_new_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT classes_s_classes_h_id_fk FOREIGN KEY (id)
        REFERENCES public.classes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT fk_classes_s_classes_h_parentid FOREIGN KEY (parentid)
        REFERENCES public.classes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS ix_classes_s_path_ids
    ON public.classes_s USING gin
    (path_ids)
    TABLESPACE pg_default;

CREATE OR REPLACE TRIGGER classes_s_insert
    AFTER INSERT
    ON public.classes_s
    FOR EACH ROW
    WHEN (pg_trigger_depth() < 1)
    EXECUTE FUNCTION public.classes_s_insert();
...