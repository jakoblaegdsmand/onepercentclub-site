
/* Views */

App.HomeBannerView = Ember.View.extend({
    templateName: 'home_banner',

    didInsertElement: function() {

        // Carousel
        this.$().find('.carousel').unslider({
            dots: true,
            fluid: true,
            delay: 10000
        });
    }
});


App.HomeProjectView = Ember.View.extend({
    templateName: 'home_project',

    didInsertElement: function() {
        var donated = this.get('controller.project.campaign.money_donated');
        var asked = this.get('controller.project.campaign.money_asked');
        this.$('.slider-progress').css('width', '0px');
        var width = 0;
        if (asked > 0) {
            width = 100 * donated / asked;
            width += '%';
        }
        this.$('.slider-progress').animate({'width': width}, 1000);
    }.observes('controller.project')
});


App.HomeQuotesView = Ember.View.extend({
    templateName: 'home_quotes',

    didInsertElement: function() {
        var controller = this.get('controller');
        this.initQuoteCycle();
    },

    initQuoteCycle: function() {
        var controller = this.get('controller');
        var view = this;

        var quoteIntervalId = setInterval(function() {
            controller.incrementProperty('quoteIndex');
            if (controller.get('quoteIndex') === controller.get('quotes').get('length')) {
                controller.set('quoteIndex', 0);
            }

            controller.loadQuote();

        }, 5000);

        this.set('quoteIntervalId', quoteIntervalId);
    },

    willDestroyElement: function() {
        clearInterval(this.get('quoteIntervalId'));
        this.set('quoteIntervalId', null);
    }
});


App.HomeImpactView = Ember.View.extend({
    templateName: 'home_impact'
});


App.HomeFundraisersView = Ember.View.extend({
    templateName: 'home_fundraisers'
});

function go(){
    $(document).bind("keydown", function(e){

        var trackOffset = $('#track').offset().left;
        if (e.keyCode == 71) {
            $('#car1').css({'left' : "+=5px"});
        }
        if (e.keyCode == 80) {
            $('#car2').css({'left' : "+=5px"});
        }

        if (($('#car2').offset().left - trackOffset) >= 1060) {
            $('#race').html("Great race! You'd be a great fund-racer too!");
            $('.message-board').css({'background-color': '#FF619A', 'color': 'white'});
            $(document).unbind("keydown");
            $('.message-board').html('PINK WINS!');
        }
        if (($('#car1').offset().left - trackOffset) >= 1060) {
            $('#race').html("Great race! You'd be a great fund-racer too!");
            $('.message-board').css({'background-color': '#00C051', 'color': 'white'});
            $(document).unbind("keydown");
            $('.message-board').html('GREEN WINS!');
        }
    });
}

var time = 10;
function countdown() {

    $('.message-board').html(time);
    if (time<=0) {
        $('.message-board').removeClass('digit');
        $('.message-board').html('GO');
        go();
    } else {
        setTimeout('countdown()', 1000);
    }
    time--;
}


App.HomeCampaignView = Ember.View.extend({
    templateName: function(){
        var homepage = this.get('controller.campaign.homepage');
        console.log(homepage);
        if (homepage == 'livestream') {
            return 'home_campaign_livestream_block';
        }
        if (homepage == 'done') {
            return 'home_campaign_done_block';
        }
        return 'home_campaign_block';
    }.property('controller.campaign.homepage'),

    didInsertElement: function() {

        // Countdown for campaign
        var deadline = this.get('controller.campaign.end');

        this.$().find('#countdown').countdown({
            until: deadline,
            format: 'HMS',
            whichLabels: null,
            timeSeparator: ':',
            layout: $('#countdown').html()
        });

        var html = '<section class="l-wrapper"><div class="hasCountdown"><span class="message-board"></span></div><h3 id="race">[P] for Pink, [G] for Green</h3><h4>Ready to race? </h4><div id="track"><div id="start"></div><div id="finish"></div><div id="car1"></div><div id="car2"></div></div></section>';

        var typeKeys = [67, 82, 65, 90, 89];
        var something_index = 0;

        $(document).bind("keydown", function (e) {
            if (e.keyCode === typeKeys[something_index++]) {
                if (something_index === typeKeys.length) {
                    $('#home-crazy-campaign-header').html(html);
                    $('.message-board').html('Get ready!');
                    setTimeout('countdown()', 2000);
                }
            } else {
                something_index = 0;
            }
        });

    }
});
