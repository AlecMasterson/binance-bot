from keras.models import Model
from keras.layers import Input, Dense, merge


def MyModel1():
    inp = Input(batch_shape=(
        None,
        32,
    ))
    out = Dense(8)(inp)
    return Model(input=inp, output=out)


def MyModel2():
    inp = Input(batch_shape=(
        None,
        10,
    ))
    out = Dense(4)(inp)
    return Model(input=inp, output=out)


def MyModel3():
    inp = Input(batch_shape=(
        None,
        12,
    ))
    out = Dense(6)(inp)
    return Model(input=inp, output=out)


model1 = MyModel1()
model2 = MyModel2()
model3 = MyModel3()

x = merge([model1.output, model2.output, model3.output], mode='concat', concat_axis=1)

x = Dense(2, activation='softmax')(x)

merged = Model(input=[model1.input, model2.input, model3.input], output=x)

merged.summary()
