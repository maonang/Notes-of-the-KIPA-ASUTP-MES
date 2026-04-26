CREATE TABLE IF NOT EXISTS public.objectprototypes_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    description character varying(255) COLLATE pg_catalog."default",
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    code character varying(255) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT objectprototypes_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT objectprototypes_s_objectprototypes_h_id_fk FOREIGN KEY (id)
        REFERENCES public.objectprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT objectprototypes_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.objectprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS objectprototypes_s_id_idx
    ON public.objectprototypes_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;

CREATE INDEX IF NOT EXISTS objectprototypes_s_parentid_index
    ON public.objectprototypes_s USING btree
    (parentid ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS objectprototypes_s_tt_idx
    ON public.objectprototypes_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...