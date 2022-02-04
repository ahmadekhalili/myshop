def categories_tree():                                            #it was better {('phone','گوشي موبايل'):dasdsad....}  (and merge with categories_tree_fa and make brife  
    return {'phone':['samsung', 'apple', 'lg'],
            'laptop':['asus'],
            'camera':['canon', 'nikon', 'sony'],
            'headphone':['sennheiser']}


def categories_tree_fa():        #dont enter letters in python api(its words is arabic... and is incorect) i input in  setmark searchbar and then copy it in python.
    return {'گوشی موبایل':[[['سامسونگ', 'samsung'], 'a'], [['ال جی', 'lg'], 'a'], [['اپل', 'apple'], 'a']],
            'لپ تاپ':[[['ایسوس', 'asus'], 'a']],
            'دوربین دیجیتال':[[['کانن', 'canon'], 'a'], [['نیکون', 'nikon'], 'a'], [['سونی', 'sony'], 'a']],
            'هدفون رو گوشی و تو گوشی':[[['سنهایزر', 'sennheiser'], 'a']]}
       

def categories_tree_searches():              #tree roots, and moadelhaiea farsi on baraie search.
    return {'phone':['گوشی', 'موبایل', 'تلفن'],
            'laptop':['لپ تاپ', 'لب تاپ', 'لب تاب'],
            'camera':['دوربین'],
            'headphone':['هدفون', 'هندزفری']}


def categories_tree_reverse():
    reverseted_category = {}
    dic = categories_tree()
    for key in dic:
        for j in dic[key]:
            reverseted_category[j] = key
    return reverseted_category

def subcategories_list():
    return [cat for key in categories_tree() for cat in categories_tree()[key]]

def fullcats_list():
    LL = [[i,*j] for i,j in categories_tree().items()]
    return [i for L in LL for i in L]
