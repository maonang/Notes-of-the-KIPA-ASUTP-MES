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

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.propertyconfigurations_s
    OWNER to "prodziiot__zif-om-object";

REVOKE ALL ON TABLE public.propertyconfigurations_s FROM prodziiot__read-role;

GRANT ALL ON TABLE public.propertyconfigurations_s TO prodziiot__debezium;

GRANT SELECT ON TABLE public.propertyconfigurations_s TO "prodziiot__read-role";

GRANT ALL ON TABLE public.propertyconfigurations_s TO "prodziiot__write-role";

GRANT ALL ON TABLE public.propertyconfigurations_s TO "prodziiot__zif-om-object";

GRANT ALL ON TABLE public.propertyconfigurations_s TO "prodziiot__zif-om-properties-view";
-- Index: propertyconfigurations_s_configuration_const_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_configuration_const_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_configuration_const_idx
    ON public.propertyconfigurations_s USING gin
    ((configuration ->> 'const'::text) COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default
    WHERE datareferenceid = 'd2073903-bbb0-46f8-af05-83c30ef5dd1b'::uuid;
-- Index: propertyconfigurations_s_configuration_expression_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_configuration_expression_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_configuration_expression_idx
    ON public.propertyconfigurations_s USING gin
    ((configuration ->> 'expression'::text) COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default
    WHERE datareferenceid = '065a9d19-259d-4293-93d2-9447e098e7b7'::uuid;
-- Index: propertyconfigurations_s_configuration_query_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_configuration_query_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_configuration_query_idx
    ON public.propertyconfigurations_s USING gin
    ((configuration ->> 'query'::text) COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default
    WHERE datareferenceid = 'b06f9e38-7bfa-449a-964b-cda145a6f648'::uuid;
-- Index: propertyconfigurations_s_configuration_tag_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_configuration_tag_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_configuration_tag_idx
    ON public.propertyconfigurations_s USING gin
    ((configuration ->> 'tagId'::text) COLLATE pg_catalog."default" gin_trgm_ops)
    TABLESPACE pg_default
    WHERE datareferenceid = '2f61cd83-0efc-4c50-b440-bcdc57a8a77a'::uuid;
-- Index: propertyconfigurations_s_id_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_id_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_id_idx
    ON public.propertyconfigurations_s USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default
    WHERE tt IS NULL AND NOT isdeleted;
-- Index: propertyconfigurations_s_tt_idx

-- DROP INDEX IF EXISTS public.propertyconfigurations_s_tt_idx;

CREATE INDEX IF NOT EXISTS propertyconfigurations_s_tt_idx
    ON public.propertyconfigurations_s USING btree
    (tt DESC NULLS FIRST)
    TABLESPACE pg_default;