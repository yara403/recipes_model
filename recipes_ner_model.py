import random
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
from entity_conversion import get_ingredient_entities_df, Entity

PATH_TO_MODEL = 'content/recipes_ner_model'
DEFAULT_SEED = 24

def create_model(train_data, validation_data, epochs):
    spacy.util.fix_random_seed(DEFAULT_SEED)
    nlp_model = spacy.blank('pt')
    
    if 'ner' not in nlp_model.pipe_names:
        nlp_model.add_pipe('ner')
    ner = nlp_model.get_pipe('ner') 

    for label in [entity_label.value for entity_label in Entity]:
        ner.add_label(label)

    optimizer = nlp_model.begin_training()
    with nlp_model.disable_pipes(*[pipe for pipe in nlp_model.pipe_names if pipe != 'ner']):
        train_examples = []
        for text, annotations in train_data:
            train_examples.append(Example.from_dict(nlp_model.make_doc(text), annotations))

        best_score = 0.0
        no_improvement_count = 0
        batch_sizes = compounding(4.0, 32.0, 1.001)
        patience = 5  # Number of epochs to wait for improvement before stopping
        for epoch in range(epochs):       
            random.shuffle(train_examples)
            losses = {}
            for batch in minibatch(train_examples, size=batch_sizes):
                nlp_model.update(
                    batch,
                    sgd=optimizer,
                    drop=0.2,
                    losses=losses
                    )

            validation_examples = []
            for text, annotations in validation_data:
                predictions = nlp_model.make_doc(text)
                example = Example.from_dict(predictions, annotations)
                validation_examples.append(example)
            results = nlp_model.evaluate(validation_examples)
            new_score = results['ents_f']
            precision = results['ents_p']
            recall = results['ents_r']
            if new_score > best_score:
                best_score = new_score
                no_improvement_count = 0
                nlp_model.to_disk(PATH_TO_MODEL)
            else:
                no_improvement_count += 1
            if no_improvement_count >= patience: # No improvement in F1-score last 5 times (patience): stop training
                break

def main():
    random.seed(DEFAULT_SEED)
    ingredient_entities_df = get_ingredient_entities_df()
    ingredients = ingredient_entities_df[['ingredients_fractional', 'entity']].values
    random.shuffle(ingredients)
    train_data = ingredients[:int(len(ingredients)*0.8)]
    validation_data = ingredients[int(len(ingredients)*0.8):]
    epochs = int(len(train_data)*0.01)  # 1% of the training data size
    create_model(train_data, validation_data, epochs)

if __name__ == "__main__":
    main()