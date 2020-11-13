\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x[0] + x[1]
Subject To
 R0: s[0] + s[1] = 1
 R1: - x[0] - y[0] + s[0] <= 0
 R2: - x[1] - y[1] + s[1] <= 0
 R3: - x[0] - y[0] - f[1,0,1] + f[1,1,0] <= 0
 R4: - f[1,0,1] + f[1,1,0] - s[0] >= 0
 R5: - 4 x[0] - 4 y[0] + f[1,0,1] + 4 s[0] <= 0
 R6: - x[1] - y[1] + f[0,0,1] - f[0,1,0] <= 0
 R7: f[0,0,1] - f[0,1,0] - s[1] >= 0
 R8: - 4 x[1] - 4 y[1] + f[0,1,0] + 4 s[1] <= 0
 R9: - 5 x[0] - 5 y[0] + f[0,0,1] + 5 s[0] <= 0
 R10: - 5 x[1] - 5 y[1] + f[1,1,0] + 5 s[1] <= 0
Bounds
 x[0] = 0
 x[1] = 0
 y[0] = 0
 y[1] = 0
Binaries
 x[0] x[1] y[0] y[1] s[0] s[1]
End
