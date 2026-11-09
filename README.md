# Campus Polling System

**Mata Kuliah:** Cloud Computing - Telkom University (Ujian Chunin / UTS)
**Studi Kasus:** #7 Sistem Polling / Voting Kampus

| Nama | NIM |
|------|-----|
| (isi) | (isi) |
| (isi) | (isi) |
| (isi) | (isi) |

## Deskripsi
Aplikasi voting sederhana (Opsi A vs B) dengan Backend Python REST API, Frontend HTML + Vanilla JS di Nginx,
dideploy memakai Docker Compose dan otomatis lewat Jenkins + GitHub Webhook.

## Diagram Arsitektur
```
 Browser :8080
     |
     v
+------------------------------ Docker Custom Bridge: app-net ------------------------------+
|  [frontend: nginx:alpine]  --- /api/* proxy (DNS: backend) --->  [backend: python app.py]  |
|        |                                                              |                   |
|   Bind Mount                                                    Named Volume              |
|   ./frontend -> /usr/share/nginx/html                polling-db-data -> /var/lib/backend_data
+--------------------------------------------------------------------------------------------+

 git push (main) --> GitHub --Webhook--> Jenkins --> Checkout > Syntax Check > Build > Deploy > Health Check
```

## API
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/votes` | Total suara, perolehan A vs B, daftar catatan |
| POST | `/votes` | Body `{"option":"A"}` atau `{"option":"B"}` (400 jika tidak valid) |
| DELETE | `/votes?index=X` | Hapus catatan suara (400 jika index salah, 404 jika tidak ada) |

Data disimpan di `votes.json` dalam Named Volume `polling-db-data`.

## Instalasi Lokal
```bash
git clone <URL_REPO>
cd campus-polling
docker compose up -d --build
# buka http://localhost:8080
```

## Uji Data Immunity
```bash
docker rm -f polling-backend
docker compose up -d
# data suara tetap ada
```

## Setup Jenkins
1. Jalankan Jenkins (lihat panduan), install plugin **GitHub** & **Pipeline**.
2. Tambah credential PAT (Kind: Username with password).
3. Buat job **Pipeline script from SCM** -> repo GitHub, branch `main`, Script Path `Jenkinsfile`.
4. Centang **GitHub hook trigger for GITScm polling**.
5. Di GitHub: Settings > Webhooks > `http://<JENKINS_URL>/github-webhook/` (Content type: application/json).

## Video Demo
(tempel tautan video 5-8 menit)
