CREATE TABLE IF NOT EXISTS public.properties_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    tt timestamp with time zone,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    isdeleted boolean NOT NULL DEFAULT false,
    valuetypeid uuid NOT NULL,
    uomid uuid NOT NULL,
    propertyprimitiveid uuid NOT NULL,
    objectid uuid NOT NULL,
    datatypeid uuid NOT NULL,
    hierarchyscopeids uuid[],
    propertytype smallint,
    path character varying COLLATE pg_catalog."default",
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    CONSTRAINT properties_s_pk_new PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT properties_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.properties_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT properties_s_properties_h_id_fk FOREIGN KEY (id)
        REFERENCES public.properties_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT properties_s_propertyprimitives_h_id_fk FOREIGN KEY (propertyprimitiveid)
        REFERENCES public.propertyprimitives_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
)
...