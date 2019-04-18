
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
    <li v-if="visibleOptions.length">
        <div
          @click="showCollapse = !showCollapse"
          :class="'facet-label has-right-badge ' + (!showCollapse ? 'collapsed' : null)"
          :aria-controls="'collapse-'+facet.name"
          :aria-expanded="showCollapse ? 'true' : 'false'"
          role="button"
        >
            <div class="d-inline-block text-truncate w-100">{{ facet.title }}</div>
            <div v-if="showCount"><span class="badge badge-pill badge-secondary">{{ checkedOptionsCount }}</span></div>
        </div>
        
        </div>
        <b-collapse v-model="showCollapse" class="facet-submenu" :id="'collapse-'+facet.name">
            <option-facet v-for="option in visibleOptions" :option="option" :facet="facet"></option-facet>
            <div class="d-flex justify-content-between">
                <b-button v-b-modal="'facetModal-'+facet.name" variant="link" size="sm" class="p-0">
                    More...
                </b-button>      
                <div>
                    <b-button v-if="facet.checkedOptions.length" variant="link" size="sm" class="p-0" @click="unselectAll()">
                       Unselect all
                    </b-button>  
                </div>                     
            </div>
        </b-collapse>
        <input v-if="facet.checkedOptions.length" type="hidden" :name="facet.name" :value="JSON.stringify(facet.checkedOptions)">
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
            additionalOptions = additionalOptions.filter(function (additionalOption, pos) {
                return !checkedOptions.some(checkedOption => checkedOption.value === additionalOption.value);
            }); // Filter out those already selected
            additionalOptions = additionalOptions.slice(0, additionalOptionsCount); // Pick only the amount needed to show at least five
            let resultOptions = this.facet.checkedOptions.concat(additionalOptions); // Merge selected and filling options
            return resultOptions;
        },
        checkedOptionsCount() {
            return this.facet.checkedOptions.length;
        },
        showCount() {
            return !this.showCollapse && this.checkedOptionsCount;
        },
    },
    data () {
        return {
            showCollapse: null,
            // @todo Save options in sidebar component not store
        }
    },
    mounted () {
        this.showCollapse = Boolean(this.checkedOptionsCount);
    },
    methods: {
        unselectAll() {
            this.facet.checkedOptions = [];
        }
    }
});

Vue.component('option-facet', {
    props: ['option', 'facet'],
    template: `
    <div class="form-check w-100 facet-option">
        <input type="checkbox"
            class="form-check-input"
            :id="'option-facet-'+uid"
            :value="option"
            :key="option.value"
            v-model="facet.checkedOptions"
        >
        <label :for="'option-facet-'+uid" class="form-check-label w-100">
            <div class="has-right-badge">
                <div class="d-inline-block text-truncate">{{ option.text }}</div>
                <div><span class="badge badge-pill badge-light">{{ option.count }}x</span></div>
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
    <b-modal :id="'facetModal-' + facet.name" size="xl" :title="facet.title" scrollable ok-only>
        <div class="in-facet-search">
            <input class="form-control form-control-sm" v-model="searchInput">
        </div>
        <div class="pt-2 facet-modal-options">
            <option-facet v-for="option in modalOptions" :option="option" :facet="facet"></option-facet>
        </div>
    </b-modal>`,
    watch: {
        searchInput(after, before) {
            this.fetchOptions();
        }
    },
    data () {
        return {
            modalOptions: [],
            searchInput: null,
        };
    },
    computed: {
        facet() {
            return store.state.facets[this.index];
        },
        esQuery() {
            return store.state.esQuery;
        },
        searchType() {
            return store.state.searchType;
        }
    },
    methods: {
        fetchOptions() {
            console.log(this.searchInput);
            axios.get('/facets/api/' + this.facet.name, {
                params:
                    {
                        search_val: this.searchInput,
                        search_dict: this.esQuery,
                        search_type: this.searchType,
                    }
                })
                .then(response => this.modalOptions = response.data)
                .catch(error => {});
        },
        resetContent() {
            this.searchInput = null;
            this.fetchOptions();
        }
    },
    mounted() {
      this.$root.$on('bv::modal::show', (bvEvent, modalId) => {
          if(modalId === 'facetModal-' + this.facet.name) // @todo not exactly the best method to listen the open event
              this.resetContent();
      })
    }
});

Vue.component('search-input', {
    props: ['old-value'],
    template: `
        <div class="input-group input-group-sm mt-3">
            <input name="query" type="text" class="form-control" placeholder="Search..." aria-label="Search" aria-describedby="basic-addon2" :value="oldValue">
            <div class="input-group-append">
                <button class="btn btn-light" type="send">Search</button>
            </div>
        </div>
    `,
    computed: {
        /*
        query() {
            let query = this.buildQuery();
            console.log(query);
            if(query === '')
                return this.oldValue;
            return this.buildQuery();
        }
        */
    },
    methods: {
        buildQuery() {
            let facetQueryArr = [];
            this.facets.forEach(function(facet) {
                if(facet.checkedOptions.length)
                {

                    let values = facet.checkedOptions.map(function(option) {
                        return option.value;
                    });
                    facetQueryArr.push(facet.field + ':("' + values.join('" OR "') + '")');
                }
            });
            if(facetQueryArr.length === 0)
                return '';
            return facetQueryArr.join(' AND ');
        }
    }
});

const store = new Vuex.Store({
    state: {
        facets: [],
        esQuery: null,
        searchType: null,
    },
    mutations: {
        initFacetsData (state, payload) {
            state.facets = payload;
        },
        initEsQuery (state, payload) {
            state.esQuery = payload;
        },
        initSearchType (state, payload) {
            state.searchType = payload;
        },
    }
});

Vue.component('init-vue-data', {
    props: ['facets', 'es', 'type', 'query'],
    template: '<div></div>',
    mounted() {
        store.commit('initFacetsData', this.facets);
        store.commit('initEsQuery', JSON.stringify(this.es));
        store.commit('initSearchType', this.type);
    }
});


var vue = new Vue({
    el: '#vue',
    store: store,
    data: {
    },
});

