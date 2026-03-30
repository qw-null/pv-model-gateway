<template>
  <div style="position: relative;" :style="{ height }">
    <!-- 加载中占位 -->
    <div
      v-if="!editorReady"
      style="height:100%; display:flex; align-items:center;
             justify-content:center; background:#1e1e1e; color:#94a3b8;
             border-radius:6px; font-size:14px;"
    >
      编辑器加载中...
    </div>
    <div
      ref="container"
      :style="{
        height: '100%',
        borderRadius: '6px',
        overflow: 'hidden',
        visibility: editorReady ? 'visible' : 'hidden'
      }"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import loader from '@monaco-editor/loader'

const props = defineProps({
  modelValue: { type: String, default: '' },
  language:   { type: String, default: 'python' },
  height:     { type: String, default: '500px' },
  readOnly:   { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const container  = ref(null)
const editorReady = ref(false)
let editor = null
let monaco = null

onMounted(async () => {
  // 使用 CDN 或本地加载 Monaco（loader 自动处理 worker）
  monaco = await loader.init()

  editor = monaco.editor.create(container.value, {
    value:                props.modelValue,
    language:             props.language,
    theme:                'vs-dark',
    fontSize:             14,
    tabSize:              4,
    automaticLayout:      true,
    minimap:              { enabled: false },
    readOnly:             props.readOnly,
    scrollBeyondLastLine: false,
    wordWrap:             'on',
  })

  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue())
  })

  editorReady.value = true
})

watch(() => props.modelValue, (val) => {
  if (editor && editor.getValue() !== val) {
    editor.setValue(val)
  }
})

onBeforeUnmount(() => {
  editor?.dispose()
})

defineExpose({
  getValue: () => editor?.getValue(),
  setValue: (v) => editor?.setValue(v),
})
</script>
