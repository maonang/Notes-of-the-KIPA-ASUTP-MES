CREATE TABLE IF NOT EXISTS public.propertyconfigurations_s
(
    id uuid NOT NULL,
    datareferenceid uuid NOT NULL,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    configuration jsonb NOT NULL,
    isgenerated boolean DEFAULT false,
    isimplemented boolean DEFAULT false,
    CONSTRAINT propertyconfigurations_s_pk PRIMARY KEY (id, datareferenceid, ts, recsrc),
    CONSTRAINT propertyconfigurations_s_property_h_id_fk FOREIGN KEY (id)
        REFERENCES public.properties_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
...