-- Table: mapping.track_points

-- DROP TABLE mapping.track_points;

CREATE TABLE mapping.track_points
(
  fid serial NOT NULL,
  ele double precision,
  "time" timestamp without time zone,
  the_geom point,
  user_id integer,
  route_id integer,
  group_id integer,
  CONSTRAINT fid_pk PRIMARY KEY (fid),
  CONSTRAINT "management.auth_group.fk" FOREIGN KEY (group_id)
      REFERENCES management.auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT "management.auth_user.fk" FOREIGN KEY (user_id)
      REFERENCES management.auth_group (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE mapping.track_points
  OWNER TO gis;
COMMENT ON TABLE mapping.track_points
  IS 'Table to hold gpx track points.';

-- Index: mapping."fid.idx"

-- DROP INDEX mapping."fid.idx";

CREATE INDEX "fid.idx"
  ON mapping.track_points
  USING btree
  (fid);

-- Index: mapping."group_id.idx"

-- DROP INDEX mapping."group_id.idx";

CREATE INDEX "group_id.idx"
  ON mapping.track_points
  USING btree
  (group_id);

-- Index: mapping."route_id.idx"

-- DROP INDEX mapping."route_id.idx";

CREATE INDEX "route_id.idx"
  ON mapping.track_points
  USING btree
  (route_id);

-- Index: mapping."the_geom.idx"

-- DROP INDEX mapping."the_geom.idx";

CREATE INDEX "the_geom.idx"
  ON mapping.track_points
  USING gist
  (the_geom);

-- Index: mapping."user_id.idx"

-- DROP INDEX mapping."user_id.idx";

CREATE INDEX "user_id.idx"
  ON mapping.track_points
  USING btree
  (user_id);

