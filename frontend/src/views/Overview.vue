<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>2025年收入追踪系统</h1>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>记录收入
        </el-button>
        <el-date-picker
          v-model="selectedDate"
          type="month"
          placeholder="选择月份"
          @change="handleDateChange"
          class="date-picker" />
      </div>
    </div>

    <!-- 顶部卡片 -->
    <div class="stat-cards">
      <div class="stat-card total">
        <div class="stat-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ totalIncome.toLocaleString() }}</div>
          <div class="stat-label">总收入</div>
        </div>
      </div>
      <div class="stat-card monthly">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ monthlyIncome.toLocaleString() }}</div>
          <div class="stat-label">本月收入</div>
          <div class="stat-trend" :class="monthlyTrend >= 0 ? 'up' : 'down'">
            <el-icon><component :is="monthlyTrend >= 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
            {{ Math.abs(monthlyTrend).toFixed(1) }}%
          </div>
        </div>
      </div>
      <div class="stat-card daily">
        <div class="stat-icon">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ dailyAverage.toLocaleString() }}</div>
          <div class="stat-label">日均收入</div>
        </div>
      </div>
      <div class="stat-card prediction">
        <div class="stat-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">¥{{ yearPrediction.toLocaleString() }}</div>
          <div class="stat-label">年度预测</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="chart-grid">
      <!-- 收入趋势图 -->
      <div class="chart-item wide">
        <div class="chart-header">
          <h3>收入趋势</h3>
          <div class="chart-actions">
            <el-radio-group v-model="trendTimeRange" size="small">
              <el-radio-button label="week">周</el-radio-button>
              <el-radio-button label="month">月</el-radio-button>
              <el-radio-button label="year">年</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div ref="trendChartRef" class="chart-container"></div>
      </div>

      <!-- 收入分布图 -->
      <div class="chart-item">
        <div class="chart-header">
          <h3>收入分布</h3>
        </div>
        <div ref="distributionChartRef" class="chart-container"></div>
      </div>

      <!-- 收入排行 -->
      <div class="chart-item">
        <div class="chart-header">
          <h3>收入排行</h3>
        </div>
        <div class="ranking-list">
          <div v-for="(type, index) in typeRanking" :key="type.value" class="ranking-item">
            <span class="ranking-index" :class="'top-' + (index + 1)">{{ index + 1 }}</span>
            <span class="ranking-label">{{ type.label }}</span>
            <span class="ranking-value">¥{{ type.amount.toLocaleString() }}</span>
            <div class="ranking-bar" :style="{ width: type.percentage + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近记录 -->
    <div class="recent-records">
      <div class="section-header">
        <h3>最近记录</h3>
        <el-button link type="primary" @click="showAllRecords">查看全部</el-button>
      </div>
      <el-table :data="recentIncomes" style="width: 100%">
        <el-table-column prop="date" label="日期" width="180">
          <template #default="{ row }">
            {{ new Date(row.date).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTagType(row.type)">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="150">
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" link @click="editIncome(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button type="danger" link @click="deleteIncome(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑收入对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑收入' : '添加收入'"
      width="500px"
      class="income-dialog">
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
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useIncomeStore } from '../store/income'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import {
  Money, Calendar, Timer, TrendCharts,
  Plus, Edit, Delete, ArrowUp, ArrowDown
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const store = useIncomeStore()
const selectedDate = ref(new Date())
const trendTimeRange = ref('month')
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const trendChartRef = ref(null)
const distributionChartRef = ref(null)

let trendChart = null
let distributionChart = null

// 收入类型定义
const incomeTypes = [
  { value: 'salary', label: '工资收入' },
  { value: 'thesis', label: '论文代写' },
  { value: 'subsidy', label: '补贴收入' },
  { value: 'other', label: '其他收入' }
]

// 表单数据
const form = ref({
  date: new Date(),
  type: '',
  amount: 0,
  description: ''
})

// 表单验证规则
const rules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  type: [{ required: true, message: '请选择收入类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }]
}

// 计算属性
const totalIncome = computed(() => store.totalIncome)

const monthlyIncome = computed(() => {
  const currentMonth = dayjs(selectedDate.value).format('YYYY-MM')
  return store.incomes
    .filter(income => dayjs(income.date).format('YYYY-MM') === currentMonth)
    .reduce((sum, income) => sum + income.amount, 0)
})

const monthlyTrend = computed(() => {
  const lastMonth = dayjs(selectedDate.value).subtract(1, 'month')
  const lastMonthIncome = store.incomes
    .filter(income => dayjs(income.date).format('YYYY-MM') === lastMonth.format('YYYY-MM'))
    .reduce((sum, income) => sum + income.amount, 0)
  
  return lastMonthIncome ? ((monthlyIncome.value - lastMonthIncome) / lastMonthIncome) * 100 : 0
})

const dailyAverage = computed(() => {
  const daysInMonth = dayjs(selectedDate.value).daysInMonth()
  return monthlyIncome.value / daysInMonth
})

const yearPrediction = computed(() => {
  const monthlyAvg = monthlyIncome.value
  return monthlyAvg * 12
})

const recentIncomes = computed(() => {
  return [...store.incomes]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5)
})

const typeRanking = computed(() => {
  const stats = {}
  incomeTypes.forEach(type => {
    stats[type.value] = 0
  })

  store.incomes.forEach(income => {
    stats[income.type] += income.amount
  })

  const total = Object.values(stats).reduce((sum, amount) => sum + amount, 0)
  
  return Object.entries(stats)
    .map(([type, amount]) => ({
      value: type,
      label: incomeTypes.find(t => t.value === type).label,
      amount,
      percentage: total ? (amount / total) * 100 : 0
    }))
    .sort((a, b) => b.amount - a.amount)
})

// 方法
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

const handleDateChange = () => {
  initCharts()
}

const openAddDialog = () => {
  isEdit.value = false
  form.value = {
    date: new Date(),
    type: '',
    amount: 0,
    description: ''
  }
  dialogVisible.value = true
}

const editIncome = (row) => {
  isEdit.value = true
  form.value = {
    ...row,
    date: new Date(row.date)
  }
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
    initCharts()
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await store.updateIncome(form.value.id, form.value)
          ElMessage.success('更新成功')
        } else {
          await store.addIncome(form.value)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        initCharts()
      } catch (error) {
        ElMessage.error(error.message)
      }
    }
  })
}

const showAllRecords = () => {
  // 可以实现查看所有记录的功能
  ElMessage.info('功能开发中')
}

// 图表初始化
const initTrendChart = () => {
  const getTimeRangeData = () => {
    const now = dayjs(selectedDate.value)
    let data = []
    let labels = []

    switch (trendTimeRange.value) {
      case 'week':
        for (let i = 0; i < 7; i++) {
          const date = now.subtract(i, 'day')
          const amount = store.incomes
            .filter(income => dayjs(income.date).format('YYYY-MM-DD') === date.format('YYYY-MM-DD'))
            .reduce((sum, income) => sum + income.amount, 0)
          data.unshift(amount)
          labels.unshift(date.format('MM-DD'))
        }
        break
      case 'month':
        const daysInMonth = now.daysInMonth()
        for (let i = 1; i <= daysInMonth; i++) {
          const date = now.date(i)
          const amount = store.incomes
            .filter(income => dayjs(income.date).format('YYYY-MM-DD') === date.format('YYYY-MM-DD'))
            .reduce((sum, income) => sum + income.amount, 0)
          data.push(amount)
          labels.push(i + '日')
        }
        break
      case 'year':
        for (let i = 0; i < 12; i++) {
          const date = now.month(i)
          const amount = store.incomes
            .filter(income => dayjs(income.date).format('YYYY-MM') === date.format('YYYY-MM'))
            .reduce((sum, income) => sum + income.amount, 0)
          data.push(amount)
          labels.push((i + 1) + '月')
        }
        break
    }

    return { data, labels }
  }

  const { data, labels } = getTimeRangeData()

  const option = {
    grid: {
      top: 40,
      right: 20,
      bottom: 40,
      left: 60
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>收入：¥{c}'
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.3)' }
      },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.3)' }
      },
      axisLabel: {
        color: 'rgba(255, 255, 255, 0.7)',
        formatter: '¥{value}'
      },
      splitLine: {
        lineStyle: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    },
    series: [{
      data: data,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        width: 3,
        color: 'var(--primary-color)'
      },
      itemStyle: {
        color: 'var(--primary-color)',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
          offset: 0,
          color: 'rgba(59, 130, 246, 0.3)'
        }, {
          offset: 1,
          color: 'rgba(59, 130, 246, 0.1)'
        }])
      }
    }]
  }

  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  trendChart.setOption(option)
}

const initDistributionChart = () => {
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        color: 'rgba(255, 255, 255, 0.7)'
      }
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#1a1a1a',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        data: typeRanking.value.map(item => ({
          name: item.label,
          value: item.amount
        }))
      }
    ]
  }

  if (!distributionChart) {
    distributionChart = echarts.init(distributionChartRef.value)
  }
  distributionChart.setOption(option)
}

const initCharts = () => {
  initTrendChart()
  initDistributionChart()
}

// 监听图表尺寸变化
watch(trendTimeRange, () => {
  initTrendChart()
})

// 生命周期钩子
onMounted(async () => {
  await store.fetchIncomes()
  initCharts()
  
  window.addEventListener('resize', () => {
    trendChart?.resize()
    distributionChart?.resize()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: 24px;
  font-weight: 500;
  background: linear-gradient(to right, var(--primary-color), #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
}

.stat-card.monthly .stat-icon {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.stat-card.daily .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.stat-card.prediction .stat-icon {
  background: linear-gradient(135deg, #6366f1, #818cf8);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.stat-trend.up {
  color: #10b981;
}

.stat-trend.down {
  color: #ef4444;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-item {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
}

.chart-item.wide {
  grid-column: span 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 500;
}

.chart-container {
  height: 300px;
}

.ranking-list {
  height: 300px;
  overflow-y: auto;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px;
  position: relative;
}

.ranking-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 12px;
}

.ranking-index.top-1 {
  background: #f59e0b;
}

.ranking-index.top-2 {
  background: #6b7280;
}

.ranking-index.top-3 {
  background: #d97706;
}

.ranking-label {
  flex: 1;
}

.ranking-value {
  margin-left: 12px;
  font-weight: 500;
}

.ranking-bar {
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  background: var(--primary-color);
  opacity: 0.2;
  transition: width 0.3s;
}

.recent-records {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 500;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style> 