create unique index if not exists plant_catalog_species_name_idx on public.plant_catalog (species_name);

insert into storage.buckets (id, name, public)
values ('plant-photos', 'plant-photos', true)
on conflict (id) do nothing;

create policy "Public can view plant photos"
on storage.objects for select
using (bucket_id = 'plant-photos');

create policy "Authenticated users can upload plant photos"
on storage.objects for insert to authenticated
with check (bucket_id = 'plant-photos');

create policy "Authenticated users can update plant photos"
on storage.objects for update to authenticated
using (bucket_id = 'plant-photos')
with check (bucket_id = 'plant-photos');

create policy "Authenticated users can delete plant photos"
on storage.objects for delete to authenticated
using (bucket_id = 'plant-photos');
