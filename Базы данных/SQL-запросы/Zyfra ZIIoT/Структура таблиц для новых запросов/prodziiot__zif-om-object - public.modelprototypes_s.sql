CREATE TABLE IF NOT EXISTS public.modelprototypes_s
(
    id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(255) COLLATE pg_catalog."default",
    code character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT modelprototypes_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT modelprototypes_s_modelprototypes_h_id_fk FOREIGN KEY (id)
        REFERENCES public.modelprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT modelprototypes_s_name_excl EXCLUDE USING btree (
        name WITH =)

        WHERE (tt IS NULL AND isdeleted = false)
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS modelprototypes_s_id_idx
    ON public.modelprototypes_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;

CREATE INDEX IF NOT EXISTS modelprototypes_s_tt_idx
    ON public.modelprototypes_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...