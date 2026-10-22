# Contributing

Discuss substantial behavior changes in an issue first. Keep pull requests focused,
use typed Python, and include tests for both accepted and rejected inputs when
adding validation. Keep README.md and README.tr.md equivalent in meaning.

```sh
python -m venv .venv
# POSIX:
. .venv/bin/activate
# PowerShell alternative: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,yaml,ffmpeg]"
git config core.hooksPath .githooks
python -m pytest -q
python -m ruff check .
python -m mypy
python -m build
```

The pre-commit hook scans staged files locally for common credential patterns.
It prints paths, never matching content. It is a baseline guard: manually review
the staged diff for personal data and credentials too. Do not bypass a failed hook.
Use Conventional Commits (`feat:`, `test:`, `docs:`, `ci:`, `fix:`).

Tests must not download models or access the network. Use invented phrases and
generated fixtures; never commit real names, phone numbers, identity numbers,
IBANs, addresses, recordings, or credentials. The optional `slow` test requires
`ALTYAZI_TEST_MODEL` (a local CTranslate2 model directory) and `ALTYAZI_TEST_AUDIO`
(a local synthetic speech file), then `python -m pytest -m slow`. It is deselected
by default and skipped without those paths. Do not include the fixtures in a PR.

If development dependencies are unavailable, the same unit tests can also run
with the standard library (pytest-specific network blocking is then absent):

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
# PowerShell:
# $env:PYTHONPATH='src'; python -m unittest discover -s tests -v
```

Report precisely which checks ran and which were blocked. Unit tests mock filesystem
I/O and recognition; they do not establish transcription accuracy or ffmpeg support.

## Releasing

To publish a new release to PyPI and GitHub:

1. Update the version number in both `pyproject.toml` (`project.version`) and `src/altyazi_tr/__init__.py` (`__version__`).
2. Update `CHANGELOG.md`: move the current `[Unreleased]` changes into a new version section with the release date, and update comparison links.
3. Commit the version bump:
   ```sh
   git commit -m "chore: release vX.Y.Z"
   ```
4. Create and push a Git tag:
   ```sh
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
5. GitHub Actions triggers `.github/workflows/release.yml` on tag push (`v*`). The workflow builds the distribution packages, validates metadata via `twine check`, publishes to PyPI via trusted publishing (`pypa/gh-action-pypi-publish`), and creates a GitHub Release with the built dist files.

## Türkçe

Büyük davranış değişikliklerini önce bir issue ile tartışalım. Değişiklikleri küçük
tutun, tip açıklamaları ekleyin, doğrulayıcılarda geçerli ve geçersiz girdileri
sınayın. İki README aynı bilgiyi taşımalı. Yukarıdaki kurulum ve kontrol komutlarını
çalıştırın; Conventional Commits biçimini kullanın.

Commit öncesi hook, hazırlanan dosyaları yerelde sır kalıplarına karşı tarar; yalnız
dosya yolunu gösterir. Eklenen içeriği kişisel veri açısından ayrıca gözden geçirin.
Engellenen hook'u atlatmayın. Testler model indirmez; yalnız uydurma cümleler ve
üretilmiş örnekler kullanın. `slow` testi için yukarıdaki iki ortam değişkenini
yerel model ve yapay konuşma dosyasına yönlendirin. Varsayılan test çalışmasında bu
test seçilmez. Fixture dosyalarını PR'a eklemeyin. Hangi kontrollerin çalıştığını,
hangilerinin engellendiğini açıkça belirtin. Birim testleri gerçek tanıma başarısını
ve ffmpeg desteğini doğrulamaz.

## Sürüm Yayınlama

Yeni bir sürümü PyPI ve GitHub üzerinde yayınlamak için:

1. Hem `pyproject.toml` (`project.version`) hem de `src/altyazi_tr/__init__.py` (`__version__`) dosyasındaki sürüm numarasını güncelleyin.
2. `CHANGELOG.md` dosyasını güncelleyin: `[Unreleased]` altındaki maddeleri yeni sürüm başlığına taşıyıp yayın tarihini ve karşılaştırma bağlantılarını ekleyin.
3. Sürüm commit'ini oluşturun:
   ```sh
   git commit -m "chore: release vX.Y.Z"
   ```
4. Sürüm etiketini oluşturup gönderin:
   ```sh
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
5. `v*` etiketi GitHub'a ulaştığında `.github/workflows/release.yml` otomatik çalışır; sdist ve wheel paketlerini derler, `twine check` ile doğrular, güvenilir yayınlama (trusted publishing) yoluyla PyPI'ye gönderir ve GitHub üzerinde paketleri ekleyerek yeni bir Release oluşturur.
