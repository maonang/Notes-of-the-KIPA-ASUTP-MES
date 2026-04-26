CREATE TABLE IF NOT EXISTS public.modelsobjects_l
(
    modelid uuid NOT NULL,
    objectid uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    CONSTRAINT modelsobjects_l_pk PRIMARY KEY (modelid, objectid, recsrc, ts),
    CONSTRAINT modelsobjects_l_model_h_id_fk FOREIGN KEY (modelid)
        REFERENCES public.models_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT modelsobjects_l_objects_h_id_fk FOREIGN KEY (objectid)
        REFERENCES public.objects_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS modelsobjects_l_objectid_index
    ON public.modelsobjects_l USING btree
    (objectid ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS modelsobjects_l_pk_tt_idx
    ON public.modelsobjects_l USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...