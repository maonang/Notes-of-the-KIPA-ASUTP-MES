CREATE TABLE IF NOT EXISTS public.models_s
(
    id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(255) COLLATE pg_catalog."default",
    code character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'code'::character varying,
    hierarchyscopeids uuid[],
    CONSTRAINT models_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT models_s_model_h_id_fk FOREIGN KEY (id)
        REFERENCES public.models_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS models_s_hierarchyscopeid_gin_idx
    ON public.models_s USING gin
    (hierarchyscopeids)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS models_s_id_idx
    ON public.models_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;

CREATE INDEX IF NOT EXISTS models_s_name_idx
    ON public.models_s USING gin
    (name COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS models_s_tt_idx
    ON public.models_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...