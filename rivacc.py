import re
import numpy as np
import pandas as pd
import os

def find_max_week_file():
    files = os.listdir(os.getcwd())
    pattern = re.compile(r'week_(\d+)\.txt')
    max_week_file = max((file for file in files if pattern.match(file)), 
                        key=lambda x: int(pattern.match(x).group(1)), 
                        default="")
    return max_week_file


with open(find_max_week_file(), 'r') as file:
    lines = file.readlines()

# Regex pattern to match variables and their values
pattern = re.compile(r'(\w+)=(.+)')

db = {}
emp = pd.DataFrame(columns =  ["name", "wage", "bonus"])
debt = pd.DataFrame(columns =  ["name", "debt"])
savings = pd.DataFrame(columns =  ["name", "savings"])
revenue = pd.DataFrame(columns =  ["name", "revenue","xp","lbound","ubound"])
market = pd.DataFrame(columns =  ["effect", "score"])

for line in lines:
    match = pattern.search(line)
    if match:
        vartype = match.group(1).split('_')[-1]
        if vartype == 'wage':
            empname = match.group(1).split('_')[0]
            wage = match.group(2)
            emp.loc[-1] = [empname, float(wage), 0]
            emp.index = emp.index + 1  # shifting index
            emp = emp.sort_index()  # sorting by index
            
        elif vartype == 'debt':
            name = match.group(1).split('_')[0]
            debtval = match.group(2)
            debt.loc[-1] = [name, float(debtval)]
            debt.index = debt.index + 1  # shifting index
            debt = debt.sort_index()  # sorting by index

            
        elif vartype == 'deposit':
            name = match.group(1).split('_')[0]
            val = match.group(2)
            savings.loc[-1] = [name, float(val)]
            savings.index = savings.index + 1  # shifting index
            savings = savings.sort_index()  # sorting by index 

        elif vartype == 'market':
            name = match.group(1).split('__')[0]
            val = match.group(2)
            market.loc[-1] = [name, float(val)]
            market.index = market.index + 1  # shifting index
            market = market.sort_index()  # sorting by index                   
            
        elif vartype == 'revenue':
            name = match.group(1).split('__')[0]
            
            s2 = match.group(2)
            pattern2 = r'([\d.]+), \((\d+),(\d+)\)'
            match2 = re.search(pattern2, s2)
            
            progress = min(float(match2.group(1)) + db['exp_gain'],1)
            lbound = float(match2.group(2))
            ubound = float(match2.group(3))
            
            
            val = (ubound+lbound)*progress
            
            revenue.loc[-1] = [name, float(val),progress,lbound,ubound]
            revenue.index = revenue.index + 1  # shifting index
            revenue = revenue.sort_index()  # sorting by index   
            
        elif match.group(1) == 'end':
            break
            
        else:
            try:
                db[match.group(1)] = float(match.group(2))
            except Exception:
                db[match.group(1)] = str(match.group(2))
                
      
#META
if type(db['weekno']) is float:
    db['weekno'] = db['weekno']+1
    output_file_path = "week_"+str(int(db['weekno']))+".txt"
else:
    db['weekno']=9999
    output_file_path = "week_"+str(int(db['weekno']))+".txt"



#INCOME      
total_income = 0
for _ , row in revenue.iterrows():
    row['revenue'] = row['revenue'] * max(np.random.normal(market['score'].sum(),db['instability']),0)
    total_income = total_income + row['revenue'] * max(np.random.normal(market['score'].sum(),db['instability']),0)


#WAGES
minwages = emp['wage'].sum()

bonus = total_income * db['bonus']
split_bonus = bonus // emp['name'].count()
emp['bonus'] = split_bonus
income = total_income - bonus - minwages

#DEBT PAYMENT
debt = debt.iloc[::-1].reset_index(drop=True)
debt_payment = db['debt_payment_pct'] * income
income = income - debt_payment
        
if debt_payment >= debt.loc[0,'debt']:
    debt_payment = debt_payment - debt.loc[0,'debt']
    income = income + debt_payment
    debt.loc[0,'debt'] = 0
else:
    debt.loc[0,'debt'] = debt.loc[0,'debt'] - debt_payment
    
    
#SAVINGS
savings = savings.iloc[::-1].reset_index(drop=True)
savings.loc[0,'savings'] = savings.loc[0,'savings'] + income
        




#WRITE FILE
lines = []
lines.append("\n#REPORT\n")
lines.append("total revenue = "+str(int(total_income))+"\n")
lines.append("revenue sources\n")
for index,row in revenue.iterrows():
    line = " > " + row['name'] + "=" + str(round(float(row['revenue']),2))+"\n" 
    lines.append(line)
lines.append("wages = "+str(-1*int(emp['wage'].sum()))+"\n")
lines.append("bonuses = "+str(-1*int(emp['bonus'].sum()))+"\n")
lines.append("debt paid = "+str(-1*int(debt_payment))+"\n")
lines.append("---------------------------------------\n")
lines.append("savings = "+str(int(income)))


lines.append("\n\n#META\n")
for key,val in db.items():
    line = key+"="+str(float(val))+"\n"
    lines.append(line)

lines.append("\n#INCOME\n")
for index,row in revenue.iterrows():
    line = row['name']+"__revenue"+"="+str(round(float(row['xp']),2))+", ("+str(int(row['lbound']))+","+str(int(row['ubound']))+")"+"\n"
    lines.append(line)    
    
lines.append("\n#WAGES\n")
for index,row in emp.iterrows():
    line = row['name']+"_wage"+"="+str(int(row['wage']))+"\n"
    lines.append(line)   

lines.append("\n#DEBT\n")
for index,row in debt.iterrows():
    line = row['name']+"_debt"+"="+str(int(row['debt']))+"\n"
    lines.append(line) 

lines.append("\n#SAVINGS\n")
for index,row in savings.iterrows():
    line = row['name']+"_deposit"+"="+str(int(row['savings']))+"\n"
    lines.append(line)        
    
lines.append("\n#EFFECTS\n")
for index,row in market.iterrows():
    line = row['effect']+"__market"+"="+str(float(row['score']))+"\n"
    lines.append(line) 
    
with open(output_file_path, 'w') as file:
    file.writelines(lines)

    
    
    
    