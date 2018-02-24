<template>
  <div v-if="langText">
    <div v-for="skill in skill_data.common" v-bind:key="'common-action:' + skill.id">
      <img v-bind:src="'/static/img/skill_icon/' + skill.icon" />
      <div v-for="action in skill.actions" v-bind:key="'action:' + action.id">
        <img v-bind:src="'/static/img/skill_icon/' + action.icon" />
        <div>
          <span> {{ langText.action[action.id] }} </span>
          <span> {{ langText.type[action.type_id] }} </span>
          <span> {{ langText.content[action.content_id] }} </span>
        </div>
        <div> {{action}} </div>
      </div>
    </div>

    <div v-for="skill in skill_data.only" v-bind:key="'only-action:' + skill.id">
      <img v-bind:src="'/static/img/skill_icon/' + skill.icon" />
      <div v-for="action in skill.actions" v-bind:key="'action:' + action.id">
        <img v-bind:src="'/static/img/skill_icon/' + action.icon" />
        <div>
          <span> {{ langText.action[action.id] }} </span>
          <span> {{ langText.type[action.type_id] }} </span>
          <span> {{ langText.content[action.content_id] }} </span>
        </div>
        <div> {{action}} </div>
      </div>
    </div>
  </div>
</template>

<script>
import skillData from '@/assets/skill_data'
import api from '@/api'

export default {
  // name: 'HelloWorld',
  data () {
    return {
      langText: null
    }
  },
  computed: {
    skill_data () {
      return skillData
    }
  },
  async mounted () {
    let v = await api.loadTextData()
    this.langText = v.data
  },
  methods: {
    getActionText (id) {
      return this.langText['action'][id]
    }
  }
}
</script>

<style scoped>
</style>
