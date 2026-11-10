# Campus Polling System

**Mata Kuliah:** Cloud Computing – Telkom University (UTS)  
**Studi Kasus:** #7 – Sistem Polling / Voting Kampus

## Anggota Kelompok

| Nama | NIM |
|---|---|
| Renizar Wendari | 101012500073 |
| Ghania Fitriasy Syifa | 101012580015 |
| Habib Abdurrahman | 101012580024 |
| Bagus Bintang Fauzi | 101012580026 |

## 1. Deskripsi Project

Campus Polling System merupakan aplikasi web sederhana untuk melakukan voting terhadap dua pilihan, yaitu Opsi A dan Opsi B.

Aplikasi dibangun menggunakan Python sebagai backend REST API (tanpa framework, hanya standard library), HTML dan Vanilla JavaScript sebagai frontend, serta Nginx sebagai web server dan reverse proxy.

Seluruh layanan dijalankan menggunakan Docker Compose dengan Custom Bridge Network. Penyimpanan data menggunakan Docker Named Volume agar data suara tetap tersimpan meskipun container backend dibuat ulang.

Proses Continuous Integration dan Continuous Deployment (CI/CD) diotomatisasi menggunakan Jenkins (berjalan sebagai container Docker) yang terintegrasi dengan GitHub Webhook.

**Repository GitHub:**  
https://github.com/Bintangajaa/campus-polling

## 2. Teknologi yang Digunakan

| Teknologi | Fungsi |
|---|---|
| Python | Backend REST API |
| HTML | Struktur halaman frontend |
| Vanilla JavaScript | Interaksi dan komunikasi dengan API (`fetch()`) |
| Nginx | Web server dan reverse proxy |
| Docker | Containerization aplikasi |
| Docker Compose | Mengelola beberapa container |
| Docker Bridge Network | Komunikasi antar-container |
| Docker Named Volume | Penyimpanan data persisten |
| GitHub | Version control dan repository |
| Jenkins | Otomatisasi CI/CD |
| GitHub Webhook | Memicu pipeline saat ada push |
| ngrok | Tunnel publik agar GitHub dapat menjangkau Jenkins di jaringan lokal |

## 3. Diagram Arsitektur

```text
                    USER / BROWSER
                          |
                          v
                  localhost:8080
                          |
                          v
        +-------------------------------------+
        |       DOCKER NETWORK: app-net       |
        |                                     |
        |  +-------------------------------+  |
        |  | FRONTEND (polling-frontend)   |  |
        |  | Nginx (nginx:alpine)          |  |
        |  |                               |  |
        |  | index.html + JavaScript       |  |
        |  |                               |  |
        |  | /api/* -> backend:5000        |  |
        |  +---------------+---------------+  |
        |                  |                  |
        |                  v                  |
        |  +-------------------------------+  |
        |  | BACKEND (polling-backend)     |  |
        |  | Python REST API               |  |
        |  | app.py                        |  |
        |  | Port 5000 (internal)          |  |
        |  +---------------+---------------+  |
        |                  |                  |
        +------------------|------------------+
                           |
                           v
                 DOCKER NAMED VOLUME
                    polling-db-data
                           |
                           v
              /var/lib/backend_data/votes.json
```

### Komponen Infrastruktur

- **Frontend:** Nginx menyajikan halaman web dari folder `frontend` (port host `8080`).
- **Reverse Proxy:** Nginx meneruskan request `/api/` ke backend menggunakan DNS service `backend`.
- **Backend:** Python menangani operasi GET, POST, dan DELETE pada data voting. Port 5000 hanya dapat diakses dari dalam network Docker.
- **Custom Bridge Network:** Menghubungkan frontend dan backend melalui jaringan `app-net`.
- **Named Volume:** Menyimpan file `votes.json` pada volume `polling-db-data` agar data tidak hilang ketika container dibuat ulang.
- **Bind Mount:** Menghubungkan folder `frontend` dan konfigurasi `nginx/default.conf` dari host ke container (read-only) sehingga perubahan UI langsung terlihat tanpa rebuild image.

## 4. Struktur Folder

```text
campus-polling/
├── backend/
│   ├── app.py
│   └── Dockerfile
├── frontend/
│   └── index.html
├── nginx/
│   └── default.conf
├── docker-compose.yml
├── Jenkinsfile
├── README.md
└── .gitignore
```

## 5. REST API

Backend menyediakan tiga endpoint utama. Frontend dan pengguna mengaksesnya melalui Nginx dengan prefix `/api/`.

| Method | Endpoint Backend | Akses melalui Nginx | Fungsi |
|---|---|---|---|
| GET | `/votes` | `http://localhost:8080/api/votes` | Mengambil jumlah suara, hasil voting, dan daftar suara |
| POST | `/votes` | `http://localhost:8080/api/votes` | Menambahkan suara baru |
| DELETE | `/votes?index=X` | `http://localhost:8080/api/votes?index=X` | Menghapus catatan suara berdasarkan index |

### Contoh Request

**POST – Menambahkan suara**

```json
{
  "option": "A"
}
```

Pilihan yang valid adalah `A` atau `B`. Respons sukses: `201 Created`.

**GET – Mengambil hasil voting**

Mengembalikan total suara, jumlah suara masing-masing pilihan, dan daftar catatan voting.

**DELETE – Menghapus suara**

```text
DELETE /api/votes?index=0
```

### Validasi API

| Kondisi | Status |
|---|---|
| Body POST bukan JSON valid | 400 |
| Field `option` bukan `A` atau `B` | 400 |
| Parameter `index` tidak diisi atau bukan angka (DELETE) | 400 |
| `index` di luar jangkauan data (DELETE) | 404 |
| Endpoint tidak dikenal | 404 |

## 6. Instalasi dan Menjalankan Aplikasi

### Persyaratan

- Docker Desktop atau Docker Engine.
- Docker Compose.
- Git.

### Langkah Instalasi

Clone repository:

```bash
git clone https://github.com/Bintangajaa/campus-polling.git
```

Masuk ke folder project:

```bash
cd campus-polling
```

Build dan jalankan aplikasi:

```bash
docker compose up -d --build
```

Periksa status container:

```bash
docker compose ps
```

Buka aplikasi melalui browser:

```text
http://localhost:8080
```

> Jangan membuka `index.html` langsung dari folder (`file://`), karena request `/api/...` hanya berfungsi melalui Nginx.

### Menghentikan Aplikasi

```bash
docker compose down
```

Perintah tersebut menghentikan dan menghapus container serta network project, tetapi tidak menghapus Named Volume.

## 7. Pengujian Persistensi Data (Data Immunity)

Pengujian dilakukan untuk memastikan data voting tetap tersimpan meskipun container backend dihapus dan dibuat kembali.

1. Kirim beberapa suara melalui UI, lalu catat total suara.
2. Hapus container backend:

   ```bash
   docker rm -f polling-backend
   ```

3. Jalankan kembali stack:

   ```bash
   docker compose up -d
   ```

4. Muat ulang `http://localhost:8080` (atau panggil `GET http://localhost:8080/api/votes`).

**Hasil pengujian:** Data voting tetap tersedia setelah container backend dibuat ulang karena data disimpan menggunakan Docker Named Volume `polling-db-data`.

## 8. Implementasi CI/CD dengan Jenkins

Project menggunakan Jenkins Declarative Pipeline yang terintegrasi dengan GitHub Webhook.

Alur otomatisasi:

```text
Developer
    |
    v
Git Push ke GitHub (Branch main)
    |
    v
GitHub Webhook  (https://<domain-ngrok>/github-webhook/)
    |
    v
ngrok tunnel -> Jenkins (localhost:9090)
    |
    v
Jenkins Pipeline
    |
    v
Checkout -> Syntax Check -> Build Image -> Automated Deployment -> Health Check
```

### Tahapan Jenkins Pipeline

| Stage | Fungsi |
|---|---|
| Checkout | Mengambil source code dari repository GitHub |
| Syntax Check | Memeriksa sintaks Python (`py_compile`) dan konfigurasi Docker Compose (`docker compose config`) |
| Build Image | Membangun Docker image backend (`docker compose build`) |
| Automated Deployment | Menjalankan atau memperbarui container (`docker compose up -d --remove-orphans`) |
| Health Check | Memastikan Nginx dapat menjangkau backend melalui `http://127.0.0.1/api/votes` dari dalam container frontend |

### Konfigurasi Jenkins

**a. Jalankan Jenkins sebagai container Docker**

Buat folder terpisah di luar repository (misalnya `C:\jenkins`) berisi dua file berikut, dan buat folder workspace `C:\jenkins-ws`.

`Dockerfile`:

```dockerfile
FROM jenkins/jenkins:lts-jdk17
USER root
RUN apt-get update && apt-get install -y ca-certificates curl gnupg python3 \
 && install -m 0755 -d /etc/apt/keyrings \
 && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
 && chmod a+r /etc/apt/keyrings/docker.asc \
 && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list \
 && apt-get update && apt-get install -y docker-ce-cli docker-compose-plugin \
 && rm -rf /var/lib/apt/lists/*
```

`docker-compose.yml`:

```yaml
name: jenkins-ci
services:
  jenkins:
    build: .
    container_name: jenkins
    user: root
    restart: unless-stopped
    ports:
      - "9090:8080"
      - "50000:50000"
    volumes:
      - jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - C:/jenkins-ws:/c/jenkins-ws
volumes:
  jenkins_home:
```

Jalankan:

```bash
docker compose up -d --build
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
docker exec jenkins git config --global --add safe.directory '*'
```

> Pada Git Bash (Windows), awali perintah `docker exec` yang memakai path dengan `MSYS_NO_PATHCONV=1`, atau gunakan PowerShell.

Buka `http://localhost:9090`, masukkan password awal, pilih **Install suggested plugins**, lalu buat user admin. Pastikan plugin Git, GitHub, dan Pipeline tersedia.

Jenkins memakai Docker milik host melalui `docker.sock`, sehingga container aplikasi dibuat langsung di Docker Desktop.

**b. Workspace pipeline**

`Jenkinsfile` memakai `customWorkspace '/c/jenkins-ws/campus-polling'`. Folder ini terhubung ke `C:\jenkins-ws` di Windows sehingga bind mount `./frontend` dan `./nginx/default.conf` pada `docker-compose.yml` dapat ditemukan oleh Docker Desktop.

**c. Credential GitHub**

1. Buat Personal Access Token (classic) dengan izin `repo` dan `admin:repo_hook`.
2. Di Jenkins: **Manage Jenkins** → **Credentials** → **Global** → **Add Credentials**.
3. Kind: **Username with password**, Username: `Bintangajaa`, Password: token PAT, ID: `github-pat`.

**d. Job Pipeline**

1. **New Item** → nama `campus-polling` → pilih **Pipeline**.
2. Pada **Build Triggers**, centang **GitHub hook trigger for GITScm polling**.
3. Pada **Pipeline**, pilih **Pipeline script from SCM**, SCM **Git**.
4. Repository URL: `https://github.com/Bintangajaa/campus-polling.git`
5. Credentials: `github-pat`
6. Branch Specifier: `*/main`
7. Script Path: `Jenkinsfile`

**e. Tunnel dan GitHub Webhook**

Karena Jenkins berjalan di jaringan lokal, GitHub membutuhkan URL publik. Gunakan ngrok (versi terbaru) pada terminal terpisah dan biarkan tetap berjalan:

```bash
ngrok config add-authtoken <TOKEN_NGROK>
ngrok http 9090
```

Di GitHub: **Settings** → **Webhooks** → **Add webhook**:

- Payload URL: `https://<domain-ngrok>/github-webhook/` (garis miring di akhir wajib ada)
- Content type: `application/json`
- Event: **Just the push event**

URL ngrok versi gratis dapat berubah setiap kali ngrok dijalankan ulang, sehingga Payload URL perlu diperbarui.

### Hasil Pengujian CI/CD

Pengujian dilakukan dengan melakukan `git push` ke branch `main`. Webhook GitHub memicu Jenkins secara otomatis, dan seluruh lima tahapan pipeline berhasil dijalankan:

- Checkout: Success
- Syntax Check: Success
- Build Image: Success
- Automated Deployment: Success
- Health Check: Success

Dengan demikian, perubahan pada repository GitHub memicu proses build, deployment, dan pemeriksaan kesehatan aplikasi secara otomatis.

## 9. Troubleshooting

| Masalah | Penyebab | Solusi |
|---|---|---|
| UI menampilkan "Failed to fetch" | `index.html` dibuka langsung dari folder (`file://`) | Buka melalui `http://localhost:8080` |
| `localhost:5000` menampilkan `Endpoint tidak ditemukan` | Backend hanya memiliki endpoint `/votes` | Normal; gunakan `/votes` atau lewat `http://localhost:8080/api/votes` |
| `docker compose up` gagal: path `backend` tidak ditemukan | Struktur folder belum sesuai | Pastikan `backend/`, `frontend/`, `nginx/` ada di root project |
| Health Check Jenkins gagal pada `localhost` | `localhost` di dalam container dapat diterjemahkan ke IPv6 | Gunakan `127.0.0.1` pada Jenkinsfile |
| Webhook GitHub menampilkan 403 | Payload URL tidak berakhir `/github-webhook/` | Perbaiki Payload URL lalu **Redeliver** |
| `ngrok` menolak dengan `ERR_NGROK_121` | Versi ngrok terlalu lama | Jalankan `ngrok update` |

## 10. Video Demo

Tautan video demonstrasi aplikasi dan implementasi CI/CD:

**[Tambahkan tautan video demo 5–8 menit di sini]**

Isi video: demonstrasi UI dan API, simulasi Data Immunity (menghapus container backend), serta simulasi CI/CD dari `git push` hingga Jenkins ter-trigger otomatis.

## 11. Kesimpulan

Campus Polling System berhasil diimplementasikan sebagai aplikasi web berbasis container dengan arsitektur frontend dan backend yang terpisah.

Docker Compose digunakan untuk mengelola layanan, Custom Bridge Network untuk komunikasi antar-container, Named Volume untuk menjaga persistensi data, serta Bind Mount untuk memudahkan perubahan file frontend.

Integrasi GitHub Webhook dengan Jenkins menjalankan lima tahapan CI/CD secara otomatis hingga Health Check berhasil.

:D