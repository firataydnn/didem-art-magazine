# Didem Art Newspaper — Kalıcı PostgreSQL

Supabase proje kimliği: `atjbktwtcveaibwuixfa`.

- Proje: `didem-art-newspaper`
- Bölge: `eu-west-1`
- Veritabanı: PostgreSQL 17
- Şema: `editorial` (özel)
- Sekiz tablo: `sources`, `intake`, `entities`, `events`, `event_entities`, `evidence`, `stories`, `assets`.
- RLS etkin, `anon` ve `authenticated` rollerine doğrudan tablo erişimi verilmedi.
- Kurulum ve tabloların varlığı Supabase üzerinden doğrulandı.

**Henüz yapılmayanlar:** GitHub Actions → Supabase kimlik doğrulamalı aktarım; otomatik veri senkronizasyonu; gazete ana sayfasına güvenli API; editör onayları. Servis anahtarları GitHub'a yazılmamalıdır.

-- Applied to Didem's Supabase project atjbktwtcveaibwuixfa on 2026-10-16.
-- Private schema; RLS enabled, no anon/authenticated grants.
-- Full migration managed in Supabase migration history:
-- create_private_art_newspaper_editorial_schema
-- Tables: sources, entities, events, event_entities, evidence, stories, assets, intake.
-- Never commit service_role keys or database passwords.
