from crewai import Task

def create_single_task(agent, user_input):
    return Task(
        description=f"Tugas kamu: Jawab pertanyaan berikut menggunakan info dari dokumen: '{user_input}'",
        expected_output="Jawaban lengkap bahasa Indonesia dengan menyertakan nama file pelengkap [File: ...]. Jika informasi sama sekali tidak ada di teks, jawab 'Maaf, info tidak ditemukan'.",
        agent=agent,
        verbose=True
    )
