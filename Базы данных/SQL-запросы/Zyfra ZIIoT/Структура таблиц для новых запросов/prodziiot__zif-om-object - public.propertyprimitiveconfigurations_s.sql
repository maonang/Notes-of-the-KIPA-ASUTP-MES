CREATE TABLE IF NOT EXISTS public.propertyprimitiveconfigurations_s
(
    id uuid NOT NULL,
    datareferenceid uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    configuration jsonb NOT NULL,
    CONSTRAINT propertyprimitiveconfigurations_s_pk PRIMARY KEY (id, datareferenceid, ts, recsrc),
    CONSTRAINT propertyprimitiveconfigurations_s_propertyprimitives_h_id_fk FOREIGN KEY (id)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)

TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS propertyprimitiveconfigurations_s_id_idx
    ON public.propertyprimitiveconfigurations_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;
...