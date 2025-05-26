import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random, math
import time




# ==== Hàm thuật toán giữ nguyên ====
def calculate_makespan(jobs, schedule, num_machines):
   job_task_idx = [0] * len(jobs) # Theo dõi bước hiện tại của mỗi job
   machine_end = [0] * num_machines # Thời điểm kết thúc của mỗi máy
   job_end = [0] * len(jobs) # Thời điểm kết thúc của mỗi job
   gantt_data = [] # Dữ liệu để vẽ biểu đồ Gantt
   
   for idx, job_id in enumerate(schedule):
       if job_task_idx[job_id] >= len(jobs[job_id]):
           continue # Đã hoàn thành tất cả các bước của job này
          
       machine, time = jobs[job_id][job_task_idx[job_id]] # Lấy thông tin máy và thời gian
       start = max(machine_end[machine], job_end[job_id]) # Thời điểm bắt đầu
      
       end = start + time # Tính thời điểm kết thúc
      # Cập nhật trạng thái
       machine_end[machine] = end
       job_end[job_id] = end
       gantt_data.append((machine, job_id, start, end, job_task_idx[job_id]))
       job_task_idx[job_id] += 1
   return max(machine_end), gantt_data




def generate_neighbor(schedule):
   # Tạo lịch trình lân cận bằng cách hoán đổi ngẫu nhiên 2 job trong lịch trình
   if len(schedule) < 2:
       return schedule
   a, b = random.sample(range(len(schedule)), 2) # Chọn 2 vị trí ngẫu nhiên
   new_schedule = schedule[:] # Tạo bản sao new_schedule
   new_schedule[a], new_schedule[b] = new_schedule[b], new_schedule[a] # Hoán đổi
   return new_schedule




def simulated_annealing(jobs, num_machines):
    # Khởi tạo lịch trình ngẫu nhiên
   schedule = []
   for job_id, job in enumerate(jobs):
       schedule += [job_id] * len(job) # Mỗi job xuất hiện số lần bằng số bước của nó
   random.shuffle(schedule)
   
   best_schedule = schedule[:]
   best_makespan, _ = calculate_makespan(jobs, best_schedule, num_machines)

   # Các tham số nhiệt độ ban đầu, tối thiểu, hệ số giảm nhiệt
   T = 100.0
   Tmin = 1e-3
   alpha = 0.97
   
   while T > Tmin:
       neighbor = generate_neighbor(schedule) # Tạo lân cận
       makespan_neighbor, _ = calculate_makespan(jobs, neighbor, num_machines)
      # Cập nhật lịch trình tốt nhất
       if makespan_neighbor < best_makespan:
           best_schedule = neighbor[:]
           best_makespan = makespan_neighbor
          
       current_makespan, _ = calculate_makespan(jobs, schedule, num_machines)
      # Quyết định chuyển sang trạng thái lân cận
       if (makespan_neighbor < current_makespan) or (
               random.random() < math.exp(-(makespan_neighbor - current_makespan) / T)):
           schedule = neighbor[:]
       T *= alpha # Giảm nhiệt độ
   return best_schedule, best_makespan




# ==== GREEDY BASELINE ====
def greedy_schedule(jobs, num_machines):
   """
   Lịch tham lam: lần lượt bước 1, bước 2,… của từng Job (round-robin).
   Trả về (schedule, makespan) – cùng format với SA.
   """
   max_steps = max(len(job) for job in jobs)
   schedule = []
   for step in range(max_steps):
       for job_id, job in enumerate(jobs):
           if step < len(job): # Nếu job này còn bước ở vị trí step
               schedule.append(job_id)
   makespan, _ = calculate_makespan(jobs, schedule, num_machines)
   return schedule, makespan




# ==== GUI ====
root = tk.Tk()
root.title("Job-Shop SA - Giao diện tối giản")


jobs = []
num_machines = 0




def setup_job_input(): # Giao diện nhập job
   global jobs, num_machines
   try:
       n_job = int(num_job_entry.get())
       n_machine = int(num_machine_entry.get())
       if n_job <= 0 or n_machine <= 0:
           raise ValueError
   except:
       messagebox.showerror("Lỗi", "Số job và số máy phải là số nguyên dương.")
       return


   jobs.clear()
   num_machines = n_machine


   # Xóa widget nhập liệu cũ
   for widget in frame_input_jobs.winfo_children():
       widget.destroy()


   job_steps_vars.clear()


   for i in range(n_job):
       frame = ttk.LabelFrame(frame_input_jobs, text=f"Job {i}")
       frame.pack(padx=5, pady=2, fill="x")
       steps_var = tk.StringVar(value="3")
       tk.Label(frame, text="Số bước: ").pack(side="left")
       entry = tk.Entry(frame, width=3, textvariable=steps_var)
       entry.pack(side="left")


       def make_callback(i, var=steps_var):
           def callback(*_):
               show_job_steps(i, int(var.get()) if var.get().isdigit() else 1)


           return callback


       steps_var.trace_add('write', make_callback(i, steps_var))
       job_steps_vars.append((steps_var, []))


       # Hiện ô nhập từng bước
       show_job_steps(i, int(steps_var.get()))



# Hiển thị ô nhập từng bước của job
def show_job_steps(job_idx, n_steps):
   # Xóa các widget nhập bước cũ
   parent = frame_input_jobs.winfo_children()[job_idx]
   for child in parent.winfo_children():
       if isinstance(child, ttk.Frame):
           child.destroy()
   step_vars = []
   for j in range(n_steps):
       frame = ttk.Frame(parent)
       frame.pack(anchor="w", padx=10, pady=1)
       tk.Label(frame, text=f"Bước {j + 1}: Máy").pack(side="left")
       machine_var = tk.StringVar(value="0")
       tk.Entry(frame, width=3, textvariable=machine_var).pack(side="left")
       tk.Label(frame, text="Thời gian").pack(side="left")
       time_var = tk.StringVar(value="1")
       tk.Entry(frame, width=4, textvariable=time_var).pack(side="left")
       step_vars.append((machine_var, time_var))
   job_steps_vars[job_idx] = (job_steps_vars[job_idx][0], step_vars)



# Lưu dữ liệu job đã nhập
def save_jobs():
   global jobs
   jobs.clear()
   for job_idx, (n_step_var, step_vars) in enumerate(job_steps_vars):
       try:
           n_steps = int(n_step_var.get())
           steps = []
           for machine_var, time_var in step_vars[:n_steps]:
               m = int(machine_var.get())
               t = int(time_var.get())
               if m < 0 or m >= num_machines or t <= 0:
                   raise ValueError
               steps.append((m, t))
           jobs.append(steps)
       except Exception as e:
           messagebox.showerror("Lỗi", f"Lỗi nhập dữ liệu job {job_idx + 1}: {e}")
           return
   messagebox.showinfo("Thông báo", "Đã lưu dữ liệu thành công!")



# Chạy thuật toán & hiển thị kết quả
def run_optimization():
   if not jobs or num_machines == 0:
       messagebox.showerror("Lỗi", "Bạn chưa nhập hoặc lưu dữ liệu job/máy.")
       return


   t0 = time.perf_counter()  ##them greddy
   schedule, makespan = simulated_annealing(jobs, num_machines)
   t_sa = time.perf_counter() - t0  ##


   # Greedy
   t0 = time.perf_counter()
   schedule_gr, makespan_gr = greedy_schedule(jobs, num_machines)
   t_gr = time.perf_counter() - t0


   # Hiển thị kết quả (ở đây chỉ dùng messagebox cho nhanh)
   msg = (
       "So sánh SA vs Greedy\n\n"
       f"SA:\n"
       f"  Lịch      : {schedule}\n"
       f"  Makespan  : {makespan}\n"
       f"  Thời gian : {t_sa:.4f}s\n\n"
       f"Greedy:\n"
       f"  Lịch      : {schedule_gr}\n"  # ← hiện thứ tự job ở đây
       f"  Makespan  : {makespan_gr}\n"
       f"  Thời gian : {t_gr:.4f}s"
   )


   messagebox.showinfo("Kết quả so sánh", msg)


   makespan_val.set(str(makespan))
   schedule_val.set(str(schedule))
   _, gantt_data = calculate_makespan(jobs, schedule, num_machines)
   update_table(gantt_data)
   draw_gantt(gantt_data)



# Cập nhật bảng kết quả 
def update_table(gantt_data):
   for row in table.get_children():
       table.delete(row)
   for record in gantt_data:
       table.insert("", "end", values=(record[1], record[4] + 1, record[0] , record[2], record[3]))



# Vẽ biểu đồ Gantt
def draw_gantt(gantt_data):
   ax.clear()
   colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:cyan']
   for record in gantt_data:
       machine, job_id, start, end, step = record
       ax.barh(machine, end - start, left=start, color=colors[job_id % len(colors)], edgecolor='black')
       ax.text((start + end) / 2, machine, f'Job{job_id }', va='center', ha='center', color='white', fontsize=9)
   ax.set_xlabel("Thời gian")
   ax.set_ylabel("Máy")
   ax.set_yticks(range(num_machines))
   ax.set_yticklabels([f'Máy {i}' for i in range(num_machines)])
   ax.set_title("Biểu đồ Gantt")
   canvas.draw()




# ==== Giao diện nhập số lượng job/máy ====
frame_top = ttk.Frame(root)
frame_top.pack(pady=4, fill="x")
ttk.Label(frame_top, text="Số job:").pack(side="left")
num_job_entry = ttk.Entry(frame_top, width=3)
num_job_entry.insert(0, "4")
num_job_entry.pack(side="left", padx=(0, 10))
ttk.Label(frame_top, text="Số máy:").pack(side="left")
num_machine_entry = ttk.Entry(frame_top, width=3)
num_machine_entry.insert(0, "3")
num_machine_entry.pack(side="left", padx=(0, 10))
ttk.Button(frame_top, text="Tạo nhập job", command=setup_job_input).pack(side="left")


frame_input_jobs = ttk.Frame(root)
frame_input_jobs.pack(pady=2, fill="x")


job_steps_vars = []


ttk.Button(root, text="Lưu dữ liệu", command=save_jobs).pack(pady=2)
ttk.Button(root, text="Chạy tối ưu", command=run_optimization).pack(pady=6)


frame_result = ttk.Frame(root)
frame_result.pack(pady=2)
ttk.Label(frame_result, text="Makespan tối ưu:").grid(row=0, column=0)
makespan_val = tk.StringVar()
ttk.Label(frame_result, textvariable=makespan_val).grid(row=0, column=1)
ttk.Label(frame_result, text="Thứ tự Job:").grid(row=1, column=0)
schedule_val = tk.StringVar()
ttk.Label(frame_result, textvariable=schedule_val).grid(row=1, column=1)


table = ttk.Treeview(root, columns=("Job", "Step", "Máy", "Start", "End"), show="headings", height=5)
for col in ("Job", "Step", "Máy", "Start", "End"):
   table.heading(col, text=col)
   table.column(col, width=60, anchor="center")
table.pack(pady=3)


fig, ax = plt.subplots(figsize=(6, 2.5))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=5)


root.mainloop()
