import json,unittest,tempfile,shutil
from decimal import Decimal
from pathlib import Path
import pyarrow.parquet as pq
from materials.physical import load_inventory
ROOT=Path(__file__).resolve().parents[1]

class InputMaterials(unittest.TestCase):
    def test_real_files_and_independent_values(self):
        records=load_inventory(ROOT/"inputs")
        self.assertTrue(records)
        seed=json.loads((ROOT/"inputs/seed.json").read_text(encoding="utf-8"))
        for name,rows in seed.items():
            self.assertEqual(pq.read_table(ROOT/"inputs"/(name+".parquet")).to_pylist(),rows)

    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/"inputs";shutil.copytree(ROOT/"inputs",target)
            inv=json.loads((target/"inventory.json").read_text(encoding="utf-8"))
            p=target/inv["files"][0]["path"];p.write_bytes(p.read_bytes()+b"x")
            with self.assertRaisesRegex(ValueError,"摘要"):load_inventory(target)

    def test_business_material_shapes(self):
        seed=json.loads((ROOT/"inputs/seed.json").read_text(encoding="utf-8"))
        actions=json.loads((ROOT/"inputs/actions.json").read_text(encoding="utf-8"))
        self.assertEqual(seed['delivery_files'][1]['encoding'],'gb18030')
        self.assertIn('gross',(ROOT/'inputs/raw/scales-a.csv').read_text(encoding='utf-8'))
        self.assertIn('V-heavy',(ROOT/'inputs/raw/scales-b.csv').read_text(encoding='gb18030'))
        self.assertEqual(seed['revisions'][0]['kind'],'cancel')

    def test_streaming_input_generation(self):
        from materials.generate import generate
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)/"raw"
            files=generate(destination,200)
            self.assertEqual(len(files),2)
            self.assertTrue((destination/"files.json").is_file())
            import csv
            with (destination/"a.csv").open(encoding="utf-8",newline="") as f:
                rows=list(csv.DictReader(f))
            self.assertGreater(len(rows),99)
            self.assertGreater(sum(r["vehicle"]=="V-heavy" for r in rows),80)
