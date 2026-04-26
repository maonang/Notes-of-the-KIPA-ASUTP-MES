CREATE TABLE IF NOT EXISTS public.classespropertyprimitives_l
(
    classid uuid NOT NULL,
    propertyprimitiveid uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    propertytype smallint,
    CONSTRAINT classespropertyprimitives_l_pk PRIMARY KEY (classid, propertyprimitiveid, ts, recsrc),
    CONSTRAINT classespropertyprimitives_l_classes_h_id_fk FOREIGN KEY (classid)
        REFERENCES public.classes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT classespropertyprimitives_l_propertyprimitives_h_id_fk FOREIGN KEY (propertyprimitiveid)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS classespropertyprimitives_l_propertyprimitiveid_index
    ON public.classespropertyprimitives_l USING btree
    (propertyprimitiveid ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS classespropertyprimitives_l_tt_idx
    ON public.classespropertyprimitives_l USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;
...