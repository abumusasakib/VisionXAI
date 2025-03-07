# **🔍 Check GPU Usage in Linux**
Run the following command **while training** to check real-time GPU utilization:
```bash
watch -n 1 nvidia-smi
```
- **Ideal:** GPU usage should be **50-100%**.  
- **Issue:** If it's stuck at **0-5%**, the GPU is **not being used effectively**.

---

For **PowerShell on Windows**, you can use the following command to monitor GPU usage in real-time:  

```powershell
while ($true) { nvidia-smi; Start-Sleep -Seconds 1; Clear-Host }
```

### **Explanation:**
- `nvidia-smi` → Fetches GPU usage stats.
- `Start-Sleep -Seconds 1` → Refreshes every **1 second**.
- `Clear-Host` → Clears the screen to show only the latest stats.

### **Alternative (Without Clearing the Screen)**
If you prefer **continuous logging** without clearing:
```powershell
while ($true) { nvidia-smi; Start-Sleep -Seconds 1 }
```

**✅ Now run this PowerShell script while your training is running to check GPU usage!** 🚀🔥