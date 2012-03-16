$(function() {

    var w = 900,
        h = 500,
        node,
        link,
        labels,
        root,
        linkIndexes;

    function tick(e) {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        
        node.attr('cx', function(d) { return d.x; })
            .attr('cy', function(d) { return d.y; });

        labels.attr('transform', function(d) {
            return 'translate(' + d.x + ',' + d.y + ')';
        });
    }

    function color(d) {
        return (d.type === 'g') ? '#3182bd' : '#c6dbef';
    }

    function typeSize(d) {
        var s;
        if (d.type === 'g') {
            s = d.count / root.maxGenreSongs;
        } else {
            s = d.count / root.maxArtistSongs;
        }
        return s;
    }

    function radius(d) {
        var r = typeSize(d);
        if (d.type === 'g') {
            r = Math.max(r * 40, 4);
        } else {
            r = Math.max(r * 25, 2);
        }
        return r;
    }

    function isConnected(a, b) {
        return linkIndexes[a.index + ',' + b.index] || a.index == b.index;
    }

    function fade(bo) {
        return function(d) {
            var opacity = bo ? 0.2 : 1;
            var rad = radius(d);

            node.style('stroke-opacity', function(o) {
                thisOpac = isConnected(d, o) ? 1 : opacity;
                this.setAttribute('fill-opacity', thisOpac);
                return thisOpac;
            });

            link.style('stroke-opacity', function(o) {
                return o.source === d || o.target === d ? 1 : opacity;
            });


            labels.select('text.label').remove();
            node.select('title').remove();
            if (bo) {
                labels.filter(function(o) {
                        return isConnected(o, d);
                    })
                    .append('svg:text')
                    .attr('y', function(o) {
                            return (o == d) ? (rad + 10) + 'px' : '5px';
                        })
                    .style('fill', '#C17021')
                    .attr('text-anchor', 'middle')
                    .attr('class', 'label')
                    .text(function(o) { return (o !== d) ? o.name.substr(0, 16) : ''; });

                node.filter(function(o) {
                        return o === d;
                    })
                    .append('title')
                    .text(function(o) { return o.name + ' / Count: ' + o.count; });
            } else {
                /*
                labels.filter(function(o) {
                        return o.type == 'g';
                    })
                    .append('svg:text')
                    .attr('y', '5px')
                    .style('fill', '#C17021')
                    .attr('text-anchor', 'middle')
                    .attr('class', 'label')
                    .text(function(o) { return o.name.substr(0, 16); })
                    .on('mouseover', function(o) {
                            d3.select(this).text('');
                        });
                */
            }
        };
    }

    var force = d3.layout.force()
        .on('tick', tick)
        .size([w, h])
        .linkDistance(20)
        //.gravity(0.05)
        .charge(function(d, i) { 
                var r = typeSize(d);
                return -r * 1000;
                //return -(1 / r) * 30; 
            });

    var vis = d3.select('#chart').append('svg:svg')
        .attr('width', w)
        .attr('height', h);

    function update() {
        // Restart the force layout
        force
            .nodes(root.nodes)
            .links(root.links)
            .start();

        //setTimeout(function() {
        //    force.stop();
        //}, 10000);

        // Update the links
        link = vis.selectAll('link.link')
            .data(root.links);

        // Enter any new links
        link.enter().append('svg:line')
            .attr('class', 'link')
            .attr('source', function(d) { return d.source; })
            .attr('target', function(d) { return d.target; });

        // Exit any old links
        link.exit().remove();

        // Update the nodes
        node = vis.selectAll('circle.node')
            .data(root.nodes);
            
        // Enter any new nodes
        node.enter().append('svg:circle')
            .attr('class', 'node')
            .attr('id', function(d) {
                    return d.type + d.id;
                })
            .style('fill', color)
            .attr('r', radius)
            .on('mouseover', fade(true))
            .on('mouseout', fade(false))
            .call(force.drag);

        // Exit any old nodes
        node.exit().remove();

        // Build fast lookup of links
        linkIndexes = {};
        root.links.forEach(function(d) {
            linkIndexes[d.source.index + ',' + d.target.index] = 1;
            linkIndexes[d.target.index + ',' + d.source.index] = 1;
        });

        // Build labels
        labels = vis.selectAll('g.labelParent')
            .data(root.nodes);

        labels.enter().append('svg:g')
            .attr('class', 'labelParent');

        labels.exit().remove();

        // Init fade state
        node.each(fade(false));
    }

    d3.json('js/music-data.json', function(json) {
        root = json;
        update();
    });

});
