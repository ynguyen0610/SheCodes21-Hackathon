create table doctor
(
    id    uuid default gen_random_uuid() not null,
    name  text                           not null,
    info  json,
    tags  text[]                         not null,
    email text                           not null,
    constraint doctor_pk
        primary key (id)
);

create unique index doctor_id_uindex
    on doctor (id);

create table post
(
    id         uuid                     default gen_random_uuid() not null,
    created_at timestamp with time zone default now()             not null,
    owner      uuid                                               not null,
    replied    text[],
    tags       text[]                                             not null,
    content    text                                               not null,
    constraint post_pk
        primary key (id),
    constraint post_doctor_id_fk
        foreign key (owner) references doctor
            on delete cascade
);

create unique index post_id_uindex
    on post (id);

create table attachment
(
    id         uuid                     default gen_random_uuid() not null,
    link       text                                               not null,
    post       uuid                                               not null,
    created_at timestamp with time zone default now()             not null,
    constraint attachment_pk
        primary key (id),
    constraint attachment_post_id_fk
        foreign key (post) references post
            on delete cascade
);

create unique index attachment_id_uindex
    on attachment (id);
