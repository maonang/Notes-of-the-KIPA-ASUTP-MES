CREATE TABLE IF NOT EXISTS public.hashtag_s
(
    id uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    description character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT hashtag_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT hashtag_s_hashtag_h_id_fk FOREIGN KEY (id)
        REFERENCES public.hashtag_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT hashtag_s_check CHECK (ts < tt OR tt IS NULL)
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS hashtag_s_id_idx
    ON public.hashtag_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;
...