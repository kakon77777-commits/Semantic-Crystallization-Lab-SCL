# Papers and Source Provenance

This directory indexes the source materials used to motivate SCL v0.1. SHA-256 digests of the exact uploaded originals are recorded in `SHA256SUMS.txt`.

## Theory papers

1. **內容信息上下界無限原理：認識論猜想 / A Conjecture on the Upper and Lower Bounds of Content-Information Infinity**  
   Original bundle filename: `Content-Information-Bounds_2026-04-25.docx`  
   EXP-0001 selects its finite Chinese source passage from this paper.

2. **程式碼替換的本體論：從語義空間到物理 manifold 的雙層無限原理 / The Ontology of Code Replacement: From Semantic Space to Physical Manifold**  
   Original bundle filename: `Ontology-of-Code-Replacement_2026-04-25.docx`  
   The source identifies Neo.K (許筌崴) with Theia, EveMissLab, dated 2026-04-25.

3. **語言同構的實驗證明：當讀者成為定理的見證者 / The Experimental Proof of Linguistic Isomorphism: When the Reader Becomes the Witness of the Theorem**  
   Original bundle filename: `Experimental-Proof-of-Linguistic-Isomorphism_2026-05-25.docx`  
   The source identifies Neo.K (許筌崴) with Theia, EveMissLab, dated 2026-05-25.

## Related implementation reference

- **EML-U MVP v0.1.0 (2026-08-18)**  
  Original bundle filename: `EML-U-MVP_v0.1.0_2026-08-18.zip`

## Binary-source note

The GitHub connector used for this synchronization can write UTF-8 repository files but does not expose a local-file binary upload parameter. Therefore this branch records exact hashes/provenance while the complete downloadable `SCL_v0.1_EXP-0001_2026-08-18.zip` contains the byte-for-byte DOCX/ZIP originals under `papers/source-original/`. No claim is made that the binary originals are already present on this GitHub branch.

SCL does not silently convert the DOCX papers into a new canonical paper source because conversion of Word equations and structured content could alter mathematical source. Any future canonical UTF-8 edition should be validated separately before being declared authoritative.
