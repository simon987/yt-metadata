-- create database "yt-meta"
-- ;

create table uploader
(
  id text not null
    constraint uploader_id_pk
    primary key,
  url text not null,
  name text not null
)
;

create unique index uploader_id_uindex
  on uploader (id)
;

create table category
(
  id serial not null
    constraint category_pkey
    primary key,
  name text not null
)
;

create table tag
(
  id serial not null
    constraint tag_pkey
    primary key,
  name text not null
)
;

create unique index tag_id_uindex
  on tag (id)
;

create table license
(
  id serial not null
    constraint license_pkey
    primary key,
  name text not null
)
;

create table video
(
  id text not null
    constraint video_pkey
    primary key,
  uploader_id text not null
    constraint video_uploader_id_fk
    references uploader,
  creator text,
  upload_date date,
  license_id integer
    constraint video_license_id_fk
    references license,
  title text,
  full_title text,
  alt_title text,
  file_name text,
  description text,
  duration integer default 0,
  age_limit integer default 0,
  annotation text,
  webpage_url text,
  view_count integer,
  like_count integer,
  dislike_count integer,
  display_id text
)
;

create unique index video_id_uindex
  on video (id)
;

create table format
(
  name text,
  note text,
  format_id text not null,
  url text,
  player_url text,
  extension text,
  audio_codec text,
  video_codec text,
  audio_bitrate integer,
  total_bitrate integer,
  file_size bigint,
  quality integer,
  width integer,
  height integer,
  fps integer,
  video_id text not null
    constraint format_video_id_fk
    references video,
  constraint format_format_id_video_id_pk
  primary key (format_id, video_id)
)
;

create table thumbnail
(
  thumbnail_id text not null,
  url text,
  video_id text not null
    constraint thumbnail_video_id_fk
    references video,
  data bytea,
  constraint thumbnail_thumbnail_id_video_id_pk
  primary key (thumbnail_id, video_id)
)
;

create table video_in_category
(
  video_id text not null
    constraint video_in_category_video_id_fk
    references video,
  category_id integer not null
    constraint video_in_category_category_id_fk
    references category
)
;

create table video_has_tag
(
  video_id text not null
    constraint video_has_tag_video_id_fk
    references video,
  tag_id integer not null
    constraint video_has_tag_tag_id_fk
    references tag
)
;

create unique index license_id_uindex
  on license (id)
;

create table subtitles
(
  language text not null,
  url text,
  data text,
  video_id text not null
    constraint subtitles_video_id_fk
    references video,
  constraint subtitles_language_video_id_pk
  primary key (language, video_id)
)
;

create table chatper
(
  id serial not null
    constraint chatper_pkey
    primary key,
  start_time integer not null,
  end_time integer not null,
  title text,
  video_id text not null
    constraint chatper_video_id_fk
    references video
)
;

create unique index chatper_id_uindex
  on chatper (id)
;

