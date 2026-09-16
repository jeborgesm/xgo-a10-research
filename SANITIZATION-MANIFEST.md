# Image Sanitization Manifest

Sanitization pass performed on the supplied repository archive.

- Raster images reviewed/metadata-stripped: **109**
- Embedded EXIF/metadata was removed from every raster image to eliminate hidden camera/location metadata.
- Shipping-label images containing personal destination information were cropped or strongly blurred while retaining manufacturer/SKU/logistics evidence where possible.
- A small set of device photos were cropped to remove unrelated printed-document background.
- Research/source/firmware/non-image files were otherwise left unchanged.

## Modified image operations

- `evidence/shipping-labels/2026-09-new-unit/IMG_8653F935-EE97-46D3-9A87-FBFE806E0647.jpeg` — **cropped**: removed US-label fragment and unrelated room/background; retained Chinese SKU/warehouse label
- `evidence/shipping-labels/2026-09-new-unit/F6B69864-0921-4860-AFC9-8BD9B70A7591.jpeg` — **cropped**: removed visible US destination/address label; retained manufacturer/product label
- `evidence/shipping-labels/2026-09-new-unit/IMG_42C47B2E-F4A0-4F50-8D7C-BE2263E9ED90.jpeg` — **cropped**: removed US destination label containing recipient/address; retained SKU/manufacturer label
- `evidence/shipping-labels/2026-09-new-unit/AE45F3BB-DCBD-4D73-8B39-2C22AAC5A596.jpeg` — **privacy blur**: obscured partial US destination ZIP/tracking barcode while preserving Chinese logistics label
- `evidence/shipping-labels/2026-09-new-unit/IMG_E8631B72-F468-4230-8A58-A5F28AB7C44C.jpeg` — **privacy blur**: obscured partial US destination/tracking strip while preserving Chinese logistics table
- `evidence/shipping-labels/2026-09-new-unit/755FA483-A224-4452-A1E6-E9E78FDC1E6F.jpeg` — **privacy blur**: obscured US shipping/tracking material while preserving Chinese logistics evidence
- `evidence/shipping-labels/2026-09-new-unit/A92E7D25-35A2-469A-BC0B-C782A86A7508.jpeg` — **privacy blur**: obscured recipient name, street address, destination, tracking number/barcode, QR code and shipment references
- `images/inbox/3c33c27b-01f7-43b4-b700-0a3a5b19baea.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/7a2c112e-178e-4a89-9b25-94ef971e918a.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/7d79cefa-49b9-4408-b7ab-1d00dd22210a.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/a1ae32c6-7cab-4508-86b0-1e3839ec66f5.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/c3353bc9-4b97-456a-af4f-724a60c569b2.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/d9d81055-ada8-42c1-96e8-98f8e573add5.jpg` — **cropped**: removed unrelated printed document/background from device photo
- `images/inbox/e6de6fdc-e951-4bd9-9885-13381fc25078.jpg` — **cropped**: removed unrelated printed document/background from device photo
