<template>
  <div class="income-entry-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>收入录入</span>
          <el-button type="primary" @click="openDialog">
            <el-icon><Plus /></el-icon>
            添加收入
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="store.loading"
        :data="store.incomes"
        style="width: 100%">
        <el-table-column prop="date" label="日期" width="180">
          <template #default="{ row }">
            {{ new Date(row.date).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="180">
          <template #default="{ row }">
            <el-tag :type="getTagType(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" size="small" @click="editIncome(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" size="small" @click="deleteIncome(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑收入' : '添加收入'"
      width="500px">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px">
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%">
          </el-date-picker>
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="form.type" placeholder="选择收入类型" style="width: 100%">
            <el-option
              v-for="type in incomeTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="0"
            :precision="2"
            :step="100"
            style="width: 100%">
          </el-input-number>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入收入描述">
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useIncomeStore } from '../store/income'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useIncomeStore()
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const incomeTypes = [
  { value: 'salary', label: '工资收入' },
  { value: 'thesis', label: '论文代写' },
  { value: 'subsidy', label: '补贴收入' },
  { value: 'other', label: '其他收入' }
]

const form = reactive({
  date: '',
  type: '',
  amount: 0,
  description: ''
})

const rules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  type: [{ required: true, message: '请选择收入类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

const getTagType = (type) => {
  const types = {
    salary: 'success',
    thesis: 'warning',
    subsidy: 'info',
    other: ''
  }
  return types[type] || ''
}

const getTypeLabel = (type) => {
  const found = incomeTypes.find(t => t.value === type)
  return found ? found.label : type
}

const openDialog = () => {
  isEdit.value = false
  form.date = new Date()
  form.type = ''
  form.amount = 0
  form.description = ''
  dialogVisible.value = true
}

const editIncome = (row) => {
  isEdit.value = true
  Object.assign(form, {
    ...row,
    date: new Date(row.date)
  })
  dialogVisible.value = true
}

const deleteIncome = (row) => {
  ElMessageBox.confirm(
    '确定要删除这条收入记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    await store.deleteIncome(row.id)
    ElMessage.success('删除成功')
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await store.updateIncome(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await store.addIncome(form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
      } catch (error) {
        ElMessage.error(error.message)
      }
    }
  })
}

// 初始化加载数据
store.fetchIncomes()
</script>

<style scoped>
.income-entry-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-input-number .el-input__wrapper) {
  width: 100%;
}
</style> 