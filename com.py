import os
from supabase import create_client, Client
from dotenv import load_dotenv
from storage3.utils import StorageException

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class communication:
	def __init__(self, table_name = None, bucket_name = None):
		self.bucket_name = bucket_name
		self.table_name = table_name
		self.response = supabase.table(self.table_name)
		self.response_bucket = supabase.table(self.bucket_name)

	def insert(self, did, uid, **kwargs):
		data = {
			"did" : did,
			"uid" : uid
		}
		data.update(kwargs)
		response = supabase.table("patient_table").insert(data).execute()

	def download(self):
		response = supabase.table("storage") \
			.select("*") \
			.eq("type", "report") \
			.order("created_at", desc=True) \
			.execute()
		name = f"{response.data[0]['file_name']}"
		try:
			with open(f"{name}.docx", "wb+") as f:
				response = supabase.storage.from_(self.bucket_name).download(
					name
				)
				f.write(response)
		except StorageException:
			print("The file doesn't exist!")

		return f"{name}.docx"


