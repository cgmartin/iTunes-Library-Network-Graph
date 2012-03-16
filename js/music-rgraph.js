$(function() {

    var w = 960,
        h = 600,
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

            node.style('stroke-opacity', function(o) {
                thisOpac = isConnected(d, o) ? 1 : opacity;
                this.setAttribute('fill-opacity', thisOpac);
                return thisOpac;
            });

            link.style('stroke-opacity', function(o) {
                return o.source === d || o.target === d ? 1 : opacity;
            });

            if (bo) {
                labels.append('svg:text')
                    .attr('y', '13px')
                    .attr('text-anchor', 'middle')
                    .text('')
                    .attr('class', 'label')
                    .style('fill-opacity', function(o) {
                        thisOpac = isConnected(d, o) ? 1 : opacity;
                        return thisOpac;
                    })
                    .text(function(o) { return isConnected(d, o) ? o.name : ''; });
            } else {
                labels.select('text.label').remove();
            }

            /*
            if (bo) {
                labels.append('svg:text')
                    .attr('y', 5)
                    .attr('text-anchor', 'middle')
                    .text(function(o) { return isConnected(d, o) && isNaN(o.name) ? o.name : ''; })
                    .attr('class', 'nodeName');
            } else {
                vis.selectAll('text.nodeName').remove('');
            }
            */
        };
    }

    var force = d3.layout.force()
        .on('tick', tick)
        .size([w, h])
        .linkDistance(30)
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

        setTimeout(function() {
            force.stop();
        }, 10000);

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
    }

    d3.json('js/music-data.json', function(json) {
        root = json;
        console.log(json);
        update();
    });


});
