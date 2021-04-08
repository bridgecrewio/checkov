var Posts = Backbone.Collection.extend({
    url: '/json/posts.json', // when we fetch, we get the JSON data Jekyll built for us
    initialize: function() {

        // here we create the index for the posts collection
        this.index = lunr(function() {
            this.field('title', {boost: 10});
            this.field('categories', {boost: 5});
            this.field('excerpt');
            this.ref('id')
        });
    },
    parse: function(posts) {
        var self = this;

        _(posts).each(function(post) {

            // add post to the lunr index
            self.index.add(post);

            // break categories apart for easier rendering in the template
            post.categories = post.categories.replace(/\s+/g, '').split(',');
        });

        // return our modified posts array
        return posts;
    },
    filter: function(term) {
        var self = this;

        // lunr returns an array of objects, we map over them and replace the lunr ref with the actual model
        var results = _(this.index.search(term)).map(function(r) {
            return self.get(r.ref);
        });

        // return the matching models from our collection
        return results;
    }
});