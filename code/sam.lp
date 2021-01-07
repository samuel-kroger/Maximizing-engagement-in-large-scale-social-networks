\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  x[Evelyn_Jefferson] + x[Laura_Mandeville] + x[Theresa_Anderson]
   + x[Brenda_Rogers] + x[Charlotte_McDowd] + x[Frances_Anderson]
   + x[Eleanor_Nye] + x[Pearl_Oglethorpe] + x[Ruth_DeSand]
   + x[Verne_Sanderson] + x[Myra_Liddel] + x[Katherina_Rogers]
   + x[Sylvia_Avondale] + x[Nora_Fayette] + x[Helen_Lloyd]
   + x[Dorothy_Murchison] + x[Olivia_Carleton] + x[Flora_Price] + x[E1]
   + x[E2] + x[E3] + x[E4] + x[E5] + x[E6] + x[E7] + x[E8] + x[E9] + x[E10]
   + x[E11] + x[E12] + x[E13] + x[E14]
Subject To
 R0: - 5 x[Evelyn_Jefferson] + x[E1] + x[E2] + x[E3] + x[E4] + x[E5]
   + x[E6] + x[E8] + x[E9] + y[E1] + y[E2] + y[E3] + y[E4] + y[E5] + y[E6]
   + y[E8] + y[E9] >= 0
 R1: - 5 x[Laura_Mandeville] + x[E1] + x[E2] + x[E3] + x[E5] + x[E6]
   + x[E7] + x[E8] + y[E1] + y[E2] + y[E3] + y[E5] + y[E6] + y[E7] + y[E8]
   >= 0
 R2: - 5 x[Theresa_Anderson] + x[E2] + x[E3] + x[E4] + x[E5] + x[E6]
   + x[E7] + x[E8] + x[E9] + y[E2] + y[E3] + y[E4] + y[E5] + y[E6] + y[E7]
   + y[E8] + y[E9] >= 0
 R3: - 5 x[Brenda_Rogers] + x[E1] + x[E3] + x[E4] + x[E5] + x[E6] + x[E7]
   + x[E8] + y[E1] + y[E3] + y[E4] + y[E5] + y[E6] + y[E7] + y[E8] >= 0
 R4: - 5 x[Katherina_Rogers] + x[E8] + x[E9] + x[E10] + x[E12] + x[E13]
   + x[E14] + y[E8] + y[E9] + y[E10] + y[E12] + y[E13] + y[E14] >= 0
 R5: - 5 x[Sylvia_Avondale] + x[E7] + x[E8] + x[E9] + x[E10] + x[E12]
   + x[E13] + x[E14] + y[E7] + y[E8] + y[E9] + y[E10] + y[E12] + y[E13]
   + y[E14] >= 0
 R6: - 5 x[Nora_Fayette] + x[E6] + x[E7] + x[E9] + x[E10] + x[E11] + x[E12]
   + x[E13] + x[E14] + y[E6] + y[E7] + y[E9] + y[E10] + y[E11] + y[E12]
   + y[E13] + y[E14] >= 0
 R7: - 5 x[Helen_Lloyd] + x[E7] + x[E8] + x[E10] + x[E11] + x[E12] + y[E7]
   + y[E8] + y[E10] + y[E11] + y[E12] >= 0
 R8: x[Evelyn_Jefferson] + x[Laura_Mandeville] + x[Theresa_Anderson]
   + x[Brenda_Rogers] + x[Charlotte_McDowd] + x[Frances_Anderson] - 5 x[E3]
   + y[Evelyn_Jefferson] + y[Laura_Mandeville] + y[Theresa_Anderson]
   + y[Brenda_Rogers] + y[Charlotte_McDowd] + y[Frances_Anderson] >= 0
 R9: x[Evelyn_Jefferson] + x[Laura_Mandeville] + x[Theresa_Anderson]
   + x[Brenda_Rogers] + x[Charlotte_McDowd] + x[Frances_Anderson]
   + x[Eleanor_Nye] + x[Ruth_DeSand] - 5 x[E5] + y[Evelyn_Jefferson]
   + y[Laura_Mandeville] + y[Theresa_Anderson] + y[Brenda_Rogers]
   + y[Charlotte_McDowd] + y[Frances_Anderson] + y[Eleanor_Nye]
   + y[Ruth_DeSand] >= 0
 R10: x[Evelyn_Jefferson] + x[Laura_Mandeville] + x[Theresa_Anderson]
   + x[Brenda_Rogers] + x[Frances_Anderson] + x[Eleanor_Nye]
   + x[Pearl_Oglethorpe] + x[Nora_Fayette] - 5 x[E6] + y[Evelyn_Jefferson]
   + y[Laura_Mandeville] + y[Theresa_Anderson] + y[Brenda_Rogers]
   + y[Frances_Anderson] + y[Eleanor_Nye] + y[Pearl_Oglethorpe]
   + y[Nora_Fayette] >= 0
 R11: x[Laura_Mandeville] + x[Theresa_Anderson] + x[Brenda_Rogers]
   + x[Charlotte_McDowd] + x[Eleanor_Nye] + x[Ruth_DeSand]
   + x[Verne_Sanderson] + x[Sylvia_Avondale] + x[Nora_Fayette]
   + x[Helen_Lloyd] - 5 x[E7] + y[Laura_Mandeville] + y[Theresa_Anderson]
   + y[Brenda_Rogers] + y[Charlotte_McDowd] + y[Eleanor_Nye]
   + y[Ruth_DeSand] + y[Verne_Sanderson] + y[Sylvia_Avondale]
   + y[Nora_Fayette] + y[Helen_Lloyd] >= 0
 R12: x[Evelyn_Jefferson] + x[Laura_Mandeville] + x[Theresa_Anderson]
   + x[Brenda_Rogers] + x[Frances_Anderson] + x[Eleanor_Nye]
   + x[Pearl_Oglethorpe] + x[Ruth_DeSand] + x[Verne_Sanderson]
   + x[Myra_Liddel] + x[Katherina_Rogers] + x[Sylvia_Avondale]
   + x[Helen_Lloyd] + x[Dorothy_Murchison] - 5 x[E8] + y[Evelyn_Jefferson]
   + y[Laura_Mandeville] + y[Theresa_Anderson] + y[Brenda_Rogers]
   + y[Frances_Anderson] + y[Eleanor_Nye] + y[Pearl_Oglethorpe]
   + y[Ruth_DeSand] + y[Verne_Sanderson] + y[Myra_Liddel]
   + y[Katherina_Rogers] + y[Sylvia_Avondale] + y[Helen_Lloyd]
   + y[Dorothy_Murchison] >= 0
 R13: x[Evelyn_Jefferson] + x[Theresa_Anderson] + x[Pearl_Oglethorpe]
   + x[Ruth_DeSand] + x[Verne_Sanderson] + x[Myra_Liddel]
   + x[Katherina_Rogers] + x[Sylvia_Avondale] + x[Nora_Fayette]
   + x[Dorothy_Murchison] + x[Olivia_Carleton] + x[Flora_Price] - 5 x[E9]
   + y[Evelyn_Jefferson] + y[Theresa_Anderson] + y[Pearl_Oglethorpe]
   + y[Ruth_DeSand] + y[Verne_Sanderson] + y[Myra_Liddel]
   + y[Katherina_Rogers] + y[Sylvia_Avondale] + y[Nora_Fayette]
   + y[Dorothy_Murchison] + y[Olivia_Carleton] + y[Flora_Price] >= 0
 R14: x[Myra_Liddel] + x[Katherina_Rogers] + x[Sylvia_Avondale]
   + x[Nora_Fayette] + x[Helen_Lloyd] - 5 x[E10] + y[Myra_Liddel]
   + y[Katherina_Rogers] + y[Sylvia_Avondale] + y[Nora_Fayette]
   + y[Helen_Lloyd] >= 0
 R15: x[Verne_Sanderson] + x[Myra_Liddel] + x[Katherina_Rogers]
   + x[Sylvia_Avondale] + x[Nora_Fayette] + x[Helen_Lloyd] - 5 x[E12]
   + y[Verne_Sanderson] + y[Myra_Liddel] + y[Katherina_Rogers]
   + y[Sylvia_Avondale] + y[Nora_Fayette] + y[Helen_Lloyd] >= 0
 R16: x[Evelyn_Jefferson] + y[Evelyn_Jefferson] <= 1
 R17: x[Laura_Mandeville] + y[Laura_Mandeville] <= 1
 R18: x[Theresa_Anderson] + y[Theresa_Anderson] <= 1
 R19: x[Brenda_Rogers] + y[Brenda_Rogers] <= 1
 R20: x[Katherina_Rogers] + y[Katherina_Rogers] <= 1
 R21: x[Sylvia_Avondale] + y[Sylvia_Avondale] <= 1
 R22: x[Nora_Fayette] + y[Nora_Fayette] <= 1
 R23: x[Helen_Lloyd] + y[Helen_Lloyd] <= 1
 R24: x[E3] + y[E3] <= 1
 R25: x[E5] + y[E5] <= 1
 R26: x[E6] + y[E6] <= 1
 R27: x[E7] + y[E7] <= 1
 R28: x[E8] + y[E8] <= 1
 R29: x[E9] + y[E9] <= 1
 R30: x[E10] + y[E10] <= 1
 R31: x[E12] + y[E12] <= 1
 R32: y[Evelyn_Jefferson] + y[Laura_Mandeville] + y[Theresa_Anderson]
   + y[Brenda_Rogers] + y[Charlotte_McDowd] + y[Frances_Anderson]
   + y[Eleanor_Nye] + y[Pearl_Oglethorpe] + y[Ruth_DeSand]
   + y[Verne_Sanderson] + y[Myra_Liddel] + y[Katherina_Rogers]
   + y[Sylvia_Avondale] + y[Nora_Fayette] + y[Helen_Lloyd]
   + y[Dorothy_Murchison] + y[Olivia_Carleton] + y[Flora_Price] + y[E1]
   + y[E2] + y[E3] + y[E4] + y[E5] + y[E6] + y[E7] + y[E8] + y[E9] + y[E10]
   + y[E11] + y[E12] + y[E13] + y[E14] <= 9
Bounds
 x[Charlotte_McDowd] = 0
 x[Frances_Anderson] = 0
 x[Eleanor_Nye] = 0
 x[Pearl_Oglethorpe] = 0
 x[Ruth_DeSand] = 0
 x[Verne_Sanderson] = 0
 x[Myra_Liddel] = 0
 x[Dorothy_Murchison] = 0
 x[Olivia_Carleton] = 0
 x[Flora_Price] = 0
 x[E1] = 0
 x[E2] = 0
 x[E4] = 0
 x[E11] = 0
 x[E13] = 0
 x[E14] = 0
Binaries
 x[Evelyn_Jefferson] x[Laura_Mandeville] x[Theresa_Anderson]
 x[Brenda_Rogers] x[Charlotte_McDowd] x[Frances_Anderson] x[Eleanor_Nye]
 x[Pearl_Oglethorpe] x[Ruth_DeSand] x[Verne_Sanderson] x[Myra_Liddel]
 x[Katherina_Rogers] x[Sylvia_Avondale] x[Nora_Fayette] x[Helen_Lloyd]
 x[Dorothy_Murchison] x[Olivia_Carleton] x[Flora_Price] x[E1] x[E2] x[E3]
 x[E4] x[E5] x[E6] x[E7] x[E8] x[E9] x[E10] x[E11] x[E12] x[E13] x[E14]
 y[Evelyn_Jefferson] y[Laura_Mandeville] y[Theresa_Anderson]
 y[Brenda_Rogers] y[Charlotte_McDowd] y[Frances_Anderson] y[Eleanor_Nye]
 y[Pearl_Oglethorpe] y[Ruth_DeSand] y[Verne_Sanderson] y[Myra_Liddel]
 y[Katherina_Rogers] y[Sylvia_Avondale] y[Nora_Fayette] y[Helen_Lloyd]
 y[Dorothy_Murchison] y[Olivia_Carleton] y[Flora_Price] y[E1] y[E2] y[E3]
 y[E4] y[E5] y[E6] y[E7] y[E8] y[E9] y[E10] y[E11] y[E12] y[E13] y[E14]
End
