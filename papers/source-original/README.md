# Binary Originals

The byte-for-byte source originals for SCL v0.1 are included in the downloadable experiment bundle generated in the ChatGPT session. Their exact SHA-256 values are listed in `../SHA256SUMS.txt`.

This GitHub branch does not contain those binary objects because the connector used for this synchronization exposes UTF-8 repository writes but no local-file binary upload parameter. The hashes make later local-git upload/verification unambiguous.
