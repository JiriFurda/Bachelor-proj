
Vue.component('sidebar-facet-list', {
    template: `<ul class="list-unstyled"><sidebar-facet v-for="(facet, index) in facets" :index="index"></sidebar-facet></ul>`,
    computed: {
        facets() {
            return store.state.facets;
        }
    }
});

Vue.component('sidebar-facet', {
    props: ['index'],
    template: `
    <li>
        <div
          @click="showCollapse = !showCollapse"
          :class="'facet-label ' + (showCollapse ? 'collapsed' : null)"
          :aria-controls="'collapse-'+facet.name"
          :aria-expanded="showCollapse ? 'true' : 'false'"
          role="button"
        >
            {{ facet.title }}
        </div>
        
        </div>
        <b-collapse v-model="showCollapse" class="facet-submenu" :id="'collapse-'+facet.name">
            <option-facet v-for="option in visibleOptions" :option="option" :facet="facet"></option-facet>
            <button type="button"
                    class="btn btn-sm btn-link more-facets"
                    title="test"
                    data-toggle="modal"
                    :data-target="'#facetModal-'+facet.name"
            >
                More...
            </button>                                
        </b-collapse>
    </li>`,
    computed: {
        facet() {
            return store.state.facets[this.index];
        },
        visibleOptions() {
            let additionalOptionsCount = Math.max(0, 5 - this.facet.checkedOptions.length); // How many options are missing to be more than five shown overall
            //let additionalOptions = this.mostFrequentOptions; // @todo Save options in sidebar component not store
            let additionalOptions = this.facet.mostFrequentOptions; // Retrieve additional options
            let checkedOptions = this.facet.checkedOptions;
            additionalOptions = additionalOptions.filter(function (item, pos) {
                return checkedOptions.indexOf(item) === -1;
            }); // Filter out those already selected
            additionalOptions = additionalOptions.slice(0, additionalOptionsCount); // Pick only the amount needed to show at least five
            let resultOptions = this.facet.checkedOptions.concat(additionalOptions); // Merge selected and filling options
            return resultOptions;
        },
    },
    data () {
        return {
            showCollapse: false,
            /* @todo Save options in sidebar component not store
            [
                {text: 'Czechia', value: 'cz'},
                {text: 'Czechia2', value: 'cz2'},
                {text: 'Czechia3', value: 'cz3'},
                {text: 'Czechia4', value: 'cz4'},
                {text: 'Czechia5', value: 'cz5'},
            ]*/
        }
    },
});

Vue.component('option-facet', {
    props: ['option', 'facet'],
    template: `
    <div class="form-check w-100">
        <input type="checkbox"
            class="form-check-input"
            :id="'option-facet-'+uid"
            :value="option"
            :key="option.value"
            :name="facet.name"
            v-model="facet.checkedOptions"
        >
        <label :for="'option-facet-'+uid" class="form-check-label w-100">
            <div class="facet-submenu-item">
                <div class="d-inline-block text-truncate">{{ option.text }}</div>
                <div><span class="badge badge-pill badge-secondary">{{ option.count }}</span></div>
            </div>
        </label>
    </div>
    `,
    data () {
        return {
            uid: null
        }
    },
    mounted () {
        this.uid = this._uid
    },
});

Vue.component('modal-facet-list', {
    template: `<div><modal-facet v-for="(facet, index) in facets" :index="index"></modal-facet></div>`, // <div v-for="facet in store.facets">TEST</div><
    computed: {
        facets() {
            return store.state.facets;
        }
    }
});

Vue.component('modal-facet', {
    props: ['index'],
    template: `
    <div class="modal fade facet-modal" :id="'facetModal-' + facet.name" tabindex="-1" role="dialog"  aria-hidden="true">
         <div class="modal-dialog modal-lg" role="document">
             <div class="modal-content">
                 <div class="modal-header">
                     <h5 class="modal-title">{{ facet.title }}</h5>
                     <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                         <span aria-hidden="true">&times;</span>
                     </button>
                 </div>
                 <div class="modal-body">
                     <div class="in-facet-search">
                         <input class="form-control form-control-sm" v-model="searchInput">
                     </div>
                     <div class="pt-2 facet-modal-options">
                        <option-facet v-for="option in facet.checkedOptions" :option="option" :facet="facet"></option-facet>
    
                         <hr>
    
                         <option-facet v-for="option in modalOptions" :option="option" :facet="facet"></option-facet>
                     </div>
                 </div>
                 <div class="modal-footer">
                     <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                     <button type="button" class="btn btn-primary">Save changes</button>
                 </div>
             </div>
         </div>
     </div>`,
    watch: {
        searchInput(after, before) {
            this.fetchOptions();
        }
    },
    data () {
        return {
            modalOptions: [
                    {text: 'Czechia', value: 'cz'},
                    {text: 'Czechia2', value: 'cz2'},
                    {text: 'Czechia3', value: 'cz3'},
                    {text: 'Czechia4', value: 'cz4'},
                    {text: 'Czechia5', value: 'cz5'},
                    {text: 'Slovakia', value: 'sk'},
                    {text: 'Netherlands', value: 'nl'},
                ],
            searchInput: null,
        };
    },
    computed: {
        facet() {
            return store.state.facets[this.index];
        },
        esQuery() {
            return store.state.esQuery;
        }
    },
    methods: {
        fetchOptions() {
            console.log(this.searchInput);
            axios.get('/facets/api/' + this.facet.name, {
                params:
                    {
                        search_val: this.searchInput,
                        search_dict: this.esQuery
                    }
                })
                .then(response => this.modalOptions = response.data)
                .catch(error => {});
        }
    }
});

const store = new Vuex.Store({
    state: {
        facets: [],
        esQuery: null
    },
    mutations: {
        initFacetsData (state, payload) {
            state.facets = payload;
        },
        initEsQuery (state, payload) {
            state.esQuery = payload;
        }
    }
});

Vue.component('init-vue-data', {
    props: ['facets', 'es'],
    template: '<div></div>',
    mounted() {
        store.commit('initFacetsData', this.facets);
        store.commit('initEsQuery', JSON.stringify(this.es));
    }
});

var vue = new Vue({
    el: '#vue',
    store: store,
    data: {
    },
});

