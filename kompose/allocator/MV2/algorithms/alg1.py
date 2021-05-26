# Resource allocation algorithm
# subject to constraints
# sell      buy
# start <   start
# end   >   end
# cpu   >   cpu*rate
# price <   price

# sell_start < buy_start < buy_end < sell_end => (allocation_start, allocation_end)
# maximizing number of trades

def matchable(buy_offer, sell_offer):
    match = False
    mediator = []

    if sell_offer.start > buy_offer.start:
        print(f"Resource not available at start")
        return match, mediator

    if sell_offer.end < buy_offer.end:
        print(f"Resource not available until end")
        return match, mediator

    if sell_offer.price > buy_offer.price:
        print("Price mismatch")
        return match, mediator

    if sell_offer.cpu < buy_offer.cpu * buy_offer.rate:
        # cycles/s   # cycles/request * requests/s
        print("Load too high")
        return match, mediator

    common_mediators = set(sell_offer.mediators).intersection(buy_offer.mediators)
    if not common_mediators:
        print("No commonly trusted Mediator")
        return match, mediator
    else:
        # print("Matchable")
        match = True
        return match, common_mediators


def construct_graph(buy_offers, sell_offers):
    graph = {}
    for i in buy_offers:
        graph[i] = set()
        edges = []

        for j in sell_offers:
            [result, mediators] = matchable(buy_offers[i], sell_offers[j])
            if result:
                graph[i].add(j)
    # print(graph)
    return graph

def get_price(buyers, sellers):
    buying = sorted(buyers.items(), key=lambda s: -s[1])
    selling = sorted(sellers.items(), key=lambda s: s[1])

    bp = buying[0][1]
    sp = selling[0][1]
    bi = 0
    si = 0

    while bp > sp:
        sp = selling[si][1]
        bp = buying[bi][1]

        print(f"bp: {bp} > sp: {sp}")

        if buying[bi+1][1] < selling[si+1][1]:
            break

        bi += 1
        si += 1

    p = (bp + sp)/2
    # p = sp

    return {
        'buyers': buying[0:bi+1],
        'sellers': selling[0:si+1],
        'price': p
    }


