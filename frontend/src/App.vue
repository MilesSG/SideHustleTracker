<template>
  <div class="app-container">
    <router-view></router-view>
  </div>
</template>

<style>
.app-container {
  min-height: 100vh;
  background-color: #1a1a1a;
  color: #fff;
}

/* 全局样式 */
:root {
  --primary-color: #3b82f6;
  --card-bg: rgba(255, 255, 255, 0.05);
  --border-color: rgba(255, 255, 255, 0.1);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Element Plus 暗色主题覆盖 */
:deep(.el-card) {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color);
  color: #fff;
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table) {
  background-color: transparent;
  color: #fff;
}

:deep(.el-table th),
:deep(.el-table tr) {
  background-color: transparent;
}

:deep(.el-table--border) {
  border-color: var(--border-color);
}

:deep(.el-table td),
:deep(.el-table th.is-leaf) {
  border-bottom: 1px solid var(--border-color);
}
</style> 