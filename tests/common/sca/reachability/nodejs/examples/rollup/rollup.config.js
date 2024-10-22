import alias from '@rollup/plugin-alias';

export default {
  plugins: [
    alias({
      entries: [
        { find: 'ax', replacement: 'axios' }
      ]
    })
  ]
};