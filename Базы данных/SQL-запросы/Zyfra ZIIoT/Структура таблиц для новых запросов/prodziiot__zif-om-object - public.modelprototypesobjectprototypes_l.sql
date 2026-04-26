CREATE TABLE IF NOT EXISTS public.modelprototypesobjectprototypes_l
(
    modelprototypeid uuid NOT NULL,
    objectprototypeid uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    CONSTRAINT modelprototypesobjectprototypes_l_pk PRIMARY KEY (modelprototypeid, objectprototypeid, ts, recsrc),
    CONSTRAINT modelprototypesobjectprototypes_l_modelprototypes_h_id_fk FOREIGN KEY (modelprototypeid)
        REFERENCES public.modelprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT modelprototypesobjectprototypes_l_objectprototypes_h_id_fk FOREIGN KEY (objectprototypeid)
        REFERENCES public.objectprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS modelprototypesobjectprototypes_l_objectprototypeid_index
    ON public.modelprototypesobjectprototypes_l USING btree
    (objectprototypeid ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS modelprototypesobjectprototypes_l_tt_idx
    ON public.modelprototypesobjectprototypes_l USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...