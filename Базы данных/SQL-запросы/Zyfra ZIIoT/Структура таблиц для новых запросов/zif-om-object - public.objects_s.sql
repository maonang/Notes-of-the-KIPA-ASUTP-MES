CREATE TABLE IF NOT EXISTS public.objects_s
(
    id uuid NOT NULL,
    parentid uuid,
    ts timestamp with time zone NOT NULL,
    recsrc character varying(255) COLLATE pg_catalog."default" NOT NULL DEFAULT 'default'::character varying,
    objectprototypeid uuid,
    tt timestamp with time zone,
    isdeleted boolean NOT NULL DEFAULT false,
    description character varying(255) COLLATE pg_catalog."default",
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    hierarchyscopeids uuid[],
    classid uuid,
    path character varying COLLATE pg_catalog."default",
    path_ids uuid[],
    path_names character varying(255)[] COLLATE pg_catalog."default",
    CONSTRAINT objects_new_s_pk PRIMARY KEY (id, ts, recsrc),
    CONSTRAINT objects_s_objectprototypeid_fkey FOREIGN KEY (objectprototypeid)
        REFERENCES public.objectprototypes_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT objects_s_objects_h_id_fk FOREIGN KEY (id)
        REFERENCES public.objects_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT objects_s_parentid_fkey FOREIGN KEY (parentid)
        REFERENCES public.objects_h (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
...