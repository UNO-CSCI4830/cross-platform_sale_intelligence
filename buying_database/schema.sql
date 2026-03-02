create table if not exists search_query (
  id bigserial primary key,
  keywords text not null,
  category_id text,
  condition_filter text,
  created_at timestamptz default now()
);

create table if not exists listing_snapshot (
  id bigserial primary key,
  search_query_id bigint references search_query(id) on delete cascade,

  ebay_item_id text not null,
  title text,

  price numeric(10,2),
  shipping numeric(10,2),
  total_price numeric(10,2),
  currency text,

  condition text,
  category_id text,
  item_url text,
  seller_username text,
  item_location text,

  captured_at timestamptz default now()
);

create index if not exists idx_listing_search_query on listing_snapshot(search_query_id);
create index if not exists idx_listing_ebay_item_id on listing_snapshot(ebay_item_id);
create index if not exists idx_listing_captured_at on listing_snapshot(captured_at);
